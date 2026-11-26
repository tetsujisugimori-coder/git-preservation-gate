"""Issue #13 comparison model. Inputs and file operations are synthetic fixtures."""
from dataclasses import dataclass
from pathlib import Path
import re

import check

LEGACY = "0.2.0"
CANDIDATE = "issue13-draft"
LOSS_RISKS = ("irrecoverable", "destructive", "strong_authenticity")
PROTECTION_KEYS = {"owner_designation", "secret", "protection_obligation", "publicly_retrievable"}


def compare(version, record, protection=None):
    """Select a contract explicitly and reuse the current evidence aggregations."""
    if version == LEGACY:
        if protection is not None:
            raise ValueError("candidate protection data requires the draft contract")
        return {"version": version, "level": record["level"], "gates": check.evaluate(record)}
    if version != CANDIDATE:
        raise ValueError("unknown contract")
    if not check.shape(record):
        raise ValueError("invalid evidence record")

    if not isinstance(protection, dict) or protection.keys() != PROTECTION_KEYS:
        raise ValueError("candidate requires an explicit protection record")
    designation = protection["owner_designation"]
    if designation is not None and (not isinstance(designation, str) or not designation.strip()):
        raise ValueError("invalid owner designation reference")
    for value in (protection[key] for key in PROTECTION_KEYS - {"owner_designation"}):
        if value is not None and type(value) is not bool:
            raise ValueError("invalid protection observation")

    risk = record["risk"]
    protected = (
        designation is not None or risk["confidential"] is True
        or protection["secret"] is True or protection["protection_obligation"] is True
    )
    uncertain_protection = any(
        value is None
        for value in (risk["confidential"], protection["secret"], protection["protection_obligation"])
    )
    if designation is not None:
        level = 3
    elif protected or uncertain_protection or any(risk[key] is None for key in LOSS_RISKS):
        level = "UNKNOWN"
    elif record["artifact_kind"] != "ordinary" or any(risk[key] for key in LOSS_RISKS):
        level = 2
    else:
        level = 1 if protection["publicly_retrievable"] is True else "UNKNOWN"

    projected = {**record, "level": level}
    if level == 2:
        # Keep actual evidence and required checks. Project only the legacy
        # automatic Level 3 triggers out of the minimum-level calculation.
        projected["risk"] = dict.fromkeys(check.RISKS, False)
        projected.pop("risk_contract", None)
        required = list(record["contract_extra_required"])
        for name, covered_by_baseline in (
            ("destructive", False),
            ("strong_authenticity", record["artifact_kind"] == "bundle"),
        ):
            if risk[name] and not covered_by_baseline:
                extra_check = name + "_protection"
                if extra_check not in required:
                    required.append(extra_check)
        projected["contract_extra_required"] = required

    # A known protection trigger takes precedence for operation stopping.
    # The legacy gate still preserves unresolved risk evidence on its own axes.
    gates = check.evaluate(projected)
    previous = check.evaluate(record)
    prior_failures = {
        axis for axis in ("custody", "verification")
        if previous[axis.upper() + "_STATUS"] == "FAIL"
    }
    reasons = set(gates["reason_codes"])
    if record.get("risk_contract", {}).get("approval") == "FAIL":
        prior_failures.add("verification")
        reasons.add("RISK_CONTRACT_APPROVAL_FAIL")
    if prior_failures:
        reasons.update(code for code in previous["reason_codes"] if code.endswith("_FAIL"))
        for axis in prior_failures:
            gates[axis.upper() + "_STATUS"] = "FAIL"
            gates["applicability"][axis] = True
            reasons.add("PRIOR_" + axis.upper() + "_FAIL")
        gates["ACCEPTANCE_STATUS"] = "FAIL"
        gates["gate_eligibility"].update(B=False, C=False)
        gates["reason_codes"] = sorted(reasons)
    return {
        "version": version,
        "level": level,
        "public_transfer_status": "BLOCKED" if protected or level == "UNKNOWN" else "NOT_TESTED",
        "gates": gates,
    }


@dataclass(frozen=True)
class ExistingCopy:
    object_id: str
    attempt_id: str
    saved_name: str
    receipt_verified: bool
    case_checks_verified: bool


@dataclass(frozen=True)
class SaveResult:
    status: str
    existing_comparison: str = "NOT_TESTED"
    confirmed_existing_name: str | None = None
    existing_attempt_id: str | None = None
    saved_name: str | None = None
    incomplete_name: str | None = None
    new_saves: int = 0
    reason: str = ""
    original_name: str | None = None
    planned_name: str | None = None
    rename_reason: str | None = None


def inspect_copy(path, original_bytes):
    try:
        if path.is_symlink() or not path.is_file():
            return "UNKNOWN"
        return "PASS" if path.read_bytes() == original_bytes else "FAIL"
    except OSError:
        return "UNKNOWN"


def save_synthetic(
    version, directory, payload, *, object_id, original_name, planned_name, alternatives,
    approved_create_names, approved_read_names, prior=None, new_save_needed=True,
    write_bytes=None,
):
    """Exercise single-file, create-only saves in the runner's private fixture directory.

    Approval and receipt fields represent fixed fixture observations. The
    optional writer lets the test interrupt an already reserved file.
    """
    if version == LEGACY:
        return SaveResult("NOT_TESTED", reason="NO_COLLISION_PROTOCOL")
    if version != CANDIDATE:
        raise ValueError("unknown contract")
    names = (planned_name, *alternatives)
    for name in (original_name, *names):
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,99}", name):
            raise ValueError("invalid fixture filename")
    if len({name.casefold() for name in names}) != len(names):
        raise ValueError("duplicate fixture filename")
    directory = Path(directory)
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("missing fixture directory")

    def outcome(status, comparison, **fields):
        return SaveResult(status, comparison, original_name=original_name, planned_name=planned_name, **fields)

    planned = directory / planned_name
    comparison = "NOT_TESTED"
    try:
        planned_collision = planned.exists() or planned.is_symlink()
    except OSError:
        return outcome("BLOCKED", comparison, reason="COLLISION_CHECK_UNAVAILABLE")
    if planned_collision and planned_name in approved_read_names:
        comparison = inspect_copy(planned, payload)
        if (
            comparison == "PASS" and prior is not None and prior.object_id == object_id
            and prior.attempt_id and prior.saved_name == planned_name and prior.receipt_verified is True and prior.case_checks_verified is True
        ):
            return outcome(
                "EXISTING_CONFIRMED", comparison, confirmed_existing_name=planned_name,
                existing_attempt_id=prior.attempt_id,
            )

    if not new_save_needed:
        return outcome("BLOCKED", comparison, reason="EXISTING_UNCONFIRMED")

    for name in names:
        if name != planned_name and not planned_collision:
            return outcome("BLOCKED", comparison, reason="PLANNED_NAME_OUTSIDE_SCOPE")
        if name not in approved_create_names or name not in approved_read_names:
            continue
        path = directory / name
        try:
            stream = path.open("xb")
        except FileExistsError:
            planned_collision = planned_collision or name == planned_name
            continue
        except OSError:
            return outcome("BLOCKED", comparison, reason="CREATE_UNAVAILABLE")
        try:
            with stream:
                if write_bytes is None:
                    stream.write(payload)
                else:
                    write_bytes(stream, payload)
            if inspect_copy(path, payload) != "PASS":
                return outcome("FAIL", comparison, incomplete_name=name, reason="READBACK_FAILED")
        except OSError:
            return outcome("FAIL", comparison, incomplete_name=name, reason="WRITE_INTERRUPTED")
        rename_reason = "PLANNED_NAME_COLLISION" if name != planned_name else None
        return outcome("NEW_SAVED", comparison, saved_name=name, new_saves=1, rename_reason=rename_reason)

    return outcome("BLOCKED", comparison, reason="NO_APPROVED_UNUSED_NAME")
