"""Compare Issue #13 §4 on the adopted model and an explicit draft selector."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from dataclasses import asdict, replace
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Barrier

from issue13_candidate import CANDIDATE, LEGACY, ExistingCopy, compare, save_synthetic

BASE = {case["id"]: case for case in json.loads(Path(__file__).with_name("cases.json").read_text())}
DEFAULT_PROTECTION = {
    "owner_designation": None,
    "secret": False,
    "protection_obligation": False,
    "publicly_retrievable": True,
}
PLANNED, ALT1, ALT2 = "original.zip", "original-1.zip", "original-2.zip"
OBJECT, PAYLOAD = "fixture-original", b"synthetic source bytes"
PRIOR = ExistingCopy(OBJECT, "prior-attempt", PLANNED, True, True)


def record(seed="V006", *, risk=None, checks=None, **fields):
    value = deepcopy(BASE[seed]["input"])
    value["risk"].update(risk or {})
    value["checks"].update(checks or {})
    return {**value, **fields}


def summary(outcome):
    gate = outcome["gates"]
    assert not any(gate["permit"].values())
    return outcome["level"], gate["VERIFICATION_STATUS"], gate["ACCEPTANCE_STATUS"]


def classify(value, old, new, *, protection=None, stop="NOT_TESTED", reason=None):
    before = deepcopy(value)
    legacy = compare(LEGACY, value)
    draft = compare(CANDIDATE, value, {**DEFAULT_PROTECTION, **(protection or {})})
    assert summary(legacy) == old, summary(legacy)
    assert summary(draft) == new, summary(draft)
    assert draft["public_transfer_status"] == stop, draft
    if reason:
        assert reason in draft["gates"]["reason_codes"], draft
    assert value == before
    return {"legacy": legacy, "candidate": draft}


def directory_snapshot(root):
    return {path.name: path.read_bytes() for path in root.iterdir()}


def collision(root, *, existing, expected, preclaimed=(), approve_create=(PLANNED, ALT1, ALT2),
              approve_read=(PLANNED, ALT1, ALT2), prior=None, new_save_needed=True,
              write_bytes=None):
    root.mkdir()
    (root / PLANNED).write_bytes(existing)
    for name in preclaimed:
        (root / name).write_bytes(b"protected prior write")
    before = directory_snapshot(root)
    fields = dict(
        object_id=OBJECT, original_name="source.zip", planned_name=PLANNED, alternatives=(ALT1, ALT2),
        approved_create_names=approve_create, approved_read_names=approve_read,
        prior=prior, new_save_needed=new_save_needed, write_bytes=write_bytes,
    )
    legacy = save_synthetic(LEGACY, root, PAYLOAD, **fields)
    assert (legacy.status, legacy.new_saves, legacy.reason) == ("NOT_TESTED", 0, "NO_COLLISION_PROTOCOL")
    assert directory_snapshot(root) == before
    draft = save_synthetic(CANDIDATE, root, PAYLOAD, **fields)
    assert (
        draft.status, draft.existing_comparison, draft.saved_name, draft.new_saves, draft.reason,
    ) == expected, draft
    assert draft.original_name == "source.zip" and draft.planned_name == PLANNED
    after = directory_snapshot(root)
    assert {name: after[name] for name in before} == before
    actual_new_files = set(after) - set(before)
    if draft.saved_name is not None:
        assert actual_new_files == {draft.saved_name} and after[draft.saved_name] == PAYLOAD
    elif draft.incomplete_name is not None:
        assert actual_new_files == {draft.incomplete_name}
    else:
        assert not actual_new_files
    return {"legacy": asdict(legacy), "candidate": asdict(draft)}



def simultaneous_creation(root):
    root.mkdir()
    start = Barrier(2, timeout=5)
    payloads = (b"synthetic writer one", b"synthetic writer two")

    def save(payload):
        start.wait()
        return save_synthetic(
            CANDIDATE, root, payload, object_id=OBJECT, original_name="source.zip", planned_name=PLANNED,
            alternatives=(ALT1,), approved_create_names=(PLANNED, ALT1),
            approved_read_names=(PLANNED, ALT1),
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(save, payload) for payload in payloads]
        outcomes = [future.result(timeout=10) for future in futures]

    assert {outcome.saved_name for outcome in outcomes} == {PLANNED, ALT1}
    assert all(outcome.status == "NEW_SAVED" and outcome.new_saves == 1 for outcome in outcomes)
    assert directory_snapshot(root) == {outcome.saved_name: payload for outcome, payload in zip(outcomes, payloads)}
    return [asdict(outcome) for outcome in outcomes]


def compare_cases(root):
    results = {}
    ordinary = record("V001")
    results["01"] = classify(ordinary, (1, "NOT_TESTED", "PASS"), (1, "NOT_TESTED", "PASS"))
    results["02"] = classify(
        record(risk={"irrecoverable": True}, checks={"bytes": "NOT_TESTED"}),
        (2, "UNKNOWN", "FAIL"), (2, "NOT_TESTED", "PARTIAL"), reason="CHECK_BYTES_NOT_TESTED",
    )
    results["03"] = classify(
        record(artifact_kind="bundle", risk={"strong_authenticity": True}, checks={"bundle_restore": "NOT_TESTED"}),
        (2, "UNKNOWN", "FAIL"), (2, "NOT_TESTED", "PARTIAL"), reason="CHECK_BUNDLE_RESTORE_NOT_TESTED",
    )
    results["04"] = classify(
        record("V001", level="UNKNOWN", risk={"confidential": None}),
        ("UNKNOWN", "UNKNOWN", "PARTIAL"), ("UNKNOWN", "UNKNOWN", "PARTIAL"), stop="BLOCKED",
    )
    results["05"] = classify(
        record("V019", risk={"confidential": True}),
        (3, "UNKNOWN", "PARTIAL"), (3, "UNKNOWN", "PARTIAL"),
        protection={"owner_designation": "synthetic-owner-record"}, stop="BLOCKED",
    )
    results["06"] = classify(
        record(risk={"confidential": True}), (2, "UNKNOWN", "FAIL"), ("UNKNOWN", "UNKNOWN", "PARTIAL"),
        protection={"secret": True}, stop="BLOCKED", reason="LEVEL_UNKNOWN",
    )
    results["07"] = classify(
        record(risk={"destructive": True}, authorization={**record()["authorization"], "scope_matches": False}),
        (2, "UNKNOWN", "FAIL"), (2, "BLOCKED", "BLOCKED"), reason="AUTH_SCOPE_MISMATCH",
    )
    results["08"] = collision(
        root / "08", existing=b"different", expected=("NEW_SAVED", "FAIL", ALT1, 1, ""),
    )
    assert results["08"]["candidate"]["rename_reason"] == "PLANNED_NAME_COLLISION"
    results["09"] = collision(
        root / "09", existing=b"different", approve_create=(PLANNED,), approve_read=(PLANNED,),
        expected=("BLOCKED", "FAIL", None, 0, "NO_APPROVED_UNUSED_NAME"),
    )
    results["10"] = collision(
        root / "10", existing=PAYLOAD, approve_create=(), approve_read=(PLANNED,), prior=PRIOR,
        expected=("EXISTING_CONFIRMED", "PASS", None, 0, ""),
    )
    assert results["10"]["candidate"]["existing_attempt_id"] == PRIOR.attempt_id
    assert results["10"]["candidate"]["confirmed_existing_name"] == PLANNED
    results["11"] = collision(
        root / "11", existing=PAYLOAD, prior=replace(PRIOR, case_checks_verified=False), new_save_needed=False,
        expected=("BLOCKED", "PASS", None, 0, "EXISTING_UNCONFIRMED"),
    )
    results["12"] = collision(
        root / "12", existing=b"different", approve_read=(ALT1,),
        expected=("NEW_SAVED", "NOT_TESTED", ALT1, 1, ""),
    )
    results["13"] = [
        collision(root / "13-next", existing=b"different", preclaimed=(ALT1,),
                  expected=("NEW_SAVED", "FAIL", ALT2, 1, "")),
        collision(root / "13-exhausted", existing=b"different", preclaimed=(ALT1,),
                  approve_create=(PLANNED, ALT1),
                  expected=("BLOCKED", "FAIL", None, 0, "NO_APPROVED_UNUSED_NAME")),
        {"simultaneous_candidate_writes": simultaneous_creation(root / "13-simultaneous")},
    ]
    results["14"] = classify(
        record(risk={"irrecoverable": True}, checks={"sha256": "FAIL"}),
        (2, "FAIL", "FAIL"), (2, "FAIL", "FAIL"), reason="CHECK_SHA256_FAIL",
    )
    results["15"] = [
        classify(ordinary, (1, "NOT_TESTED", "PASS"), (1, "NOT_TESTED", "PASS")),
        classify(record(risk={"confidential": True}), (2, "UNKNOWN", "FAIL"), ("UNKNOWN", "UNKNOWN", "PARTIAL"),
                 stop="BLOCKED"),
    ]
    historic = record(
        level=3, risk={"irrecoverable": True},
        risk_contract={"decision": "not_required", "risks": ["irrecoverable"], "approval": "PASS",
                       "rationale": "fixed synthetic historical approval"},
    )
    results["16"] = classify(historic, (3, "PASS", "PASS"), (2, "PASS", "PASS"))
    assert compare(LEGACY, historic) == results["16"]["legacy"]
    return results


def interrupt(stream, payload):
    stream.write(payload[:3])
    raise OSError("synthetic write interruption")


def boundary_cases(root):
    interrupted = collision(
        root / "interrupted", existing=b"different", write_bytes=interrupt,
        expected=("FAIL", "FAIL", None, 0, "WRITE_INTERRUPTED"),
    )
    assert interrupted["candidate"]["incomplete_name"] == ALT1
    assert (root / "interrupted" / ALT1).read_bytes() == PAYLOAD[:3]
    wrong_receipt = collision(
        root / "wrong-receipt", existing=PAYLOAD, prior=replace(PRIOR, saved_name=ALT1), new_save_needed=False,
        expected=("BLOCKED", "PASS", None, 0, "EXISTING_UNCONFIRMED"),
    )
    no_read = collision(
        root / "no-read", existing=b"different", approve_create=(ALT1,), approve_read=(PLANNED,),
        expected=("BLOCKED", "FAIL", None, 0, "NO_APPROVED_UNUSED_NAME"),
    )
    uncertain = classify(
        record(artifact_kind="bundle", risk={"irrecoverable": True}),
        (2, "UNKNOWN", "FAIL"), ("UNKNOWN", "UNKNOWN", "PARTIAL"),
        protection={"protection_obligation": None}, stop="BLOCKED",
    )
    duty = classify(
        record(), (2, "PASS", "PASS"), ("UNKNOWN", "UNKNOWN", "PARTIAL"),
        protection={"protection_obligation": True}, stop="BLOCKED",
    )
    insufficient_protection = classify(
        record(risk={"destructive": True}), (2, "UNKNOWN", "FAIL"), (2, "BLOCKED", "BLOCKED"),
        reason="EXTRA_CHECK_MISSING_destructive_protection",
    )
    return dict(interrupted=interrupted, wrong_receipt=wrong_receipt, no_read=no_read,
                uncertain=uncertain, duty=duty, insufficient_protection=insufficient_protection)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scratch-parent", type=Path)
    args = parser.parse_args()
    with TemporaryDirectory(prefix="issue13-synthetic-", dir=args.scratch_parent) as root:
        root = Path(root)
        cases = compare_cases(root)
        boundaries = boundary_cases(root)
    report = {
        "cases": cases, "boundaries": boundaries, "passed": len(cases),
        "boundaries_passed": len(boundaries), "production_permit": False,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
