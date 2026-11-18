"""Run every fixture in a subprocess and compare its result with the frozen oracle."""

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PRIMARY = {f"AT{i:02}" for i in range(1, 13)}


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def case_entry(case_id, variant, fixture=None, expected=None):
    return {
        "case": case_id, "variant": variant, "input": fixture, "expected": expected,
        "started_at": None, "ended_at": None, "exit_code": None, "stdout": "", "stderr": "",
        "actual": None, "exception": None, "test_status": "NOT_TESTED",
    }


def run_case(case_id, variant, fixture, expected):
    entry = case_entry(case_id, variant, fixture, expected)
    entry["started_at"] = timestamp()
    try:
        result = subprocess.run(
            [sys.executable, "-I", str(ROOT / "check.py"), str(ROOT / "fixtures.json"), case_id, variant],
            capture_output=True, text=True, encoding="utf-8", timeout=10, check=False,
        )
        entry.update(exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr)
        if result.returncode == 0:
            entry["actual"] = json.loads(result.stdout)
        if result.returncode != 0 and "Traceback" in result.stderr:
            entry["exception"] = result.stderr.rstrip().splitlines()[-1]
        entry["test_status"] = "PASS" if result.returncode == 0 and not result.stderr and entry["actual"] == expected else "FAIL"
    except subprocess.TimeoutExpired as exc:
        entry.update(test_status="BLOCKED", exception=str(exc),
                     stdout=(exc.stdout or b"").decode("utf-8", "replace"),
                     stderr=(exc.stderr or b"").decode("utf-8", "replace"))
    except OSError as exc:
        entry.update(test_status="BLOCKED", exception=str(exc))
    except (UnicodeError, ValueError) as exc:
        entry.update(test_status="FAIL", exception=str(exc))
    entry["ended_at"] = timestamp()
    return entry


def validate_inventory(cases, oracle):
    if not isinstance(cases, dict) or not isinstance(oracle, dict) or set(oracle) != set(cases) or not PRIMARY <= set(cases):
        raise ValueError("Fixture and oracle inventories disagree or a required case is missing")
    for case_id, variants in cases.items():
        required = {"normal", "fault"} if case_id in PRIMARY else {"additional"}
        if any(not isinstance(group, dict) or set(group) != required for group in (variants, oracle[case_id])):
            raise ValueError(f"Incorrect variant inventory for {case_id}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", required=True, type=Path)
    args = parser.parse_args()
    started_at = timestamp()
    log = {
        "started_at": started_at, "environment": {"os": platform.platform(), "python": sys.version},
        "input_sha256": {}, "preflight_error": None, "runs": [],
    }
    try:
        files = {}
        for name in ("check.py", "run.py", "fixtures.json", "oracle.json"):
            files[name] = (ROOT / name).read_bytes()
            log["input_sha256"][name] = hashlib.sha256(files[name]).hexdigest()
        cases, oracle = (json.loads(files[name]) for name in ("fixtures.json", "oracle.json"))
        validate_inventory(cases, oracle)
    except (OSError, UnicodeError, ValueError) as exc:
        log["preflight_error"] = str(exc)
        log["runs"] = [case_entry(case_id, variant) for case_id in sorted(PRIMARY) for variant in ("normal", "fault")]
    else:
        for case_id, variants in cases.items():
            for variant, fixture in variants.items():
                log["runs"].append(run_case(case_id, variant, fixture, oracle[case_id][variant]))
    log["ended_at"] = timestamp()
    for row in log["runs"]:
        print(f"{row['case']:28} {row['variant']:10} {row['test_status']}")
    args.log.parent.mkdir(parents=True, exist_ok=True)
    with args.log.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(log, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    if log["preflight_error"] is not None:
        print(log["preflight_error"], file=sys.stderr)
        return 2
    return 0 if all(row["test_status"] == "PASS" for row in log["runs"]) else 1


if __name__ == "__main__":
    sys.exit(main())
