"""Evaluate synthetic observations only. This module has no Git or custody access."""

import hashlib
import json
import re
import sys
from pathlib import Path


CHAT_SURFACES = {"web", "desktop", "mobile"}
SEVERITY = {"FAIL": 0, "BLOCKED": 1, "UNKNOWN": 2}


def nonblank(value):
    return isinstance(value, str) and bool(value.strip())


def classify(product, surface, site):
    if product == "ChatGPT" and surface in CHAT_SURFACES:
        return f"CHAT-{surface.upper()}"
    if product == "Work":
        if site == "local":
            return "WORK-LOCAL"
        if site == "cloud" and surface in CHAT_SURFACES:
            return f"WORK-CLOUD-{surface.upper()}"
    if product == "Codex" and site in {"local", "cloud"}:
        return f"CODEX-{site.upper()}"
    if product == "DOT":
        return "DOT"
    return None


def observed_class(record, evidence, issue):
    actor = evidence.get("actor")
    environment = evidence.get("environment")
    if not actor:
        issue("BLOCKED", "ACTOR_EVIDENCE_MISSING")
    if not environment:
        issue("BLOCKED", "ENVIRONMENT_EVIDENCE_MISSING")
    if not actor or not environment:
        return None
    if actor != [record["product"], record["surface"]] or environment != record["site"]:
        issue("FAIL", "OBSERVATION_MISMATCH")
        return None
    inferred = classify(*actor, environment)
    if inferred is None:
        reason = "EXECUTION_SITE_UNOBSERVED" if environment == "unknown" else "CLASSIFICATION_UNRESOLVED"
        issue("UNKNOWN", reason)
    elif inferred != record["declared"]:
        issue("FAIL", "ACTOR_CONTRADICTION")
    return inferred


def task_key(record):
    return record["repository"], record["task_id"]


def check_history(records, prior, issue):
    current_by_record = {record["record_id"]: record for record in records}
    prior_attempts = {
        (task_key(record), record["attempt_id"]): record.get("retry_of_attempt_id")
        for record in prior
    }
    retry_links = {}
    for record in prior:
        if current_by_record.get(record["record_id"]) != record:
            issue("FAIL", "PRIOR_RECORD_REMOVED_OR_CHANGED")
    for record in records:
        previous_attempt = record.get("retry_of_attempt_id")
        key = task_key(record)
        attempt = (key, record["attempt_id"])
        if attempt in prior_attempts and prior_attempts[attempt] != previous_attempt:
            issue("FAIL", "RETRY_ATTEMPT_REUSED")
        if retry_links.setdefault(attempt, previous_attempt) != previous_attempt:
            issue("FAIL", "RETRY_LINK_MISMATCH")
        if previous_attempt is None:
            continue
        if record["attempt_id"] == previous_attempt:
            issue("FAIL", "RETRY_ATTEMPT_REUSED")
        if (key, previous_attempt) not in prior_attempts:
            issue("BLOCKED", "RETRY_BASELINE_MISSING")


def check_delegation(fixture, by_execution, issue):
    parents = {}
    handoffs = {(item["parent"], item["child"]) for item in fixture.get("handoffs", []) if nonblank(item.get("ref"))}
    for execution, record in by_execution.items():
        parent = record.get("parent_execution_id")
        if parent is None:
            continue
        if parent not in by_execution:
            issue("BLOCKED", "PARENT_EXECUTION_MISSING")
            continue
        parents[execution] = parent
        if task_key(record) != task_key(by_execution[parent]):
            issue("FAIL", "PARENT_SCOPE_MISMATCH")
        if (parent, execution) not in handoffs:
            issue("BLOCKED", "HANDOFF_EVIDENCE_MISSING")
    for execution in parents:
        visited = set()
        while execution in parents:
            if execution in visited:
                issue("FAIL", "PARENT_CYCLE")
                break
            visited.add(execution)
            execution = parents[execution]
    for item in fixture.get("delegations", []):
        if item["parent"] not in by_execution:
            issue("BLOCKED", "PARENT_EXECUTION_MISSING")
        if item["child"] not in by_execution:
            issue("BLOCKED", "DELEGATED_CHILD_MISSING")
        elif parents.get(item["child"]) != item["parent"]:
            issue("FAIL", "DELEGATION_LINK_MISMATCH")


def check_audit(audit, evidence, records_by_id, issue):
    if audit is None:
        return "NOT_TESTED"
    findings = []
    roles = ("producer", "custodian", "reviewer")
    claimed = tuple(audit.get(role) for role in roles)
    verified = tuple(evidence.get("responsible", {}).get(role) for role in roles)
    if not all(nonblank(value) for value in (*claimed, *verified)):
        findings.append(("BLOCKED", "RESPONSIBLE_ACTOR_UNVERIFIED"))
    elif claimed != verified:
        findings.append(("FAIL", "RESPONSIBLE_ACTOR_MISMATCH"))
    elif verified[-1] in verified[:2]:
        findings.append(("FAIL", "SAME_RESPONSIBLE_ACTOR"))
    if "shared" not in evidence:
        findings.append(("BLOCKED", "SHARING_UNOBSERVED"))
    elif set(evidence["shared"]) - set(audit.get("declared_shared", [])):
        findings.append(("FAIL", "SHARING_UNDISCLOSED"))
    isolation_disproved_or_missing = audit.get("isolated_destination") is not True
    if audit.get("route") == "workspace_copy":
        findings.append(("FAIL", "WORKSPACE_COPY"))
    elif audit.get("route") != "approved_source":
        findings.append(("BLOCKED", "SOURCE_RETRIEVAL_REQUIRED"))
    else:
        approval, retrieval = evidence.get("approval", {}), evidence.get("retrieval", {})
        keys = ("source", "version", "sha256")
        approved_object = tuple(approval.get(key) for key in keys)
        retrieved_object = tuple(retrieval.get(key) for key in keys)
        target_keys = ("repository", "commit", "tree", "execution_id")
        record = records_by_id.get(audit.get("target_record_id"))
        target = {key: record[key] for key in target_keys} if record else None
        if (not all(nonblank(value) for value in (*approved_object, *retrieved_object, retrieval.get("retriever")))
                or not approval.get("target") or not retrieval.get("target") or target is None):
            findings.append(("BLOCKED", "SOURCE_PROOF_REQUIRED"))
        elif any(not re.fullmatch(r"[0-9a-f]{64}", item["sha256"]) for item in (approval, retrieval)):
            findings.append(("FAIL", "SOURCE_DIGEST_INVALID"))
        elif (approved_object != retrieved_object or approval["target"] != target or retrieval["target"] != target
                or (verified[-1] and retrieval["retriever"] != verified[-1])):
            findings.append(("FAIL", "SOURCE_PROOF_MISMATCH"))
        destination = retrieval.get("destination")
        if not nonblank(destination) or destination == retrieval.get("source") or retrieval.get("isolated_destination") is not True:
            isolation_disproved_or_missing = True
    if isolation_disproved_or_missing:
        findings.append(("BLOCKED", "ISOLATED_DESTINATION_REQUIRED"))
    for finding in findings:
        issue(*finding)
    return aggregate(status for status, _ in findings)


def check_receipt(example, records_by_id, issue):
    if example is None:
        return
    record_bytes = example["record_bytes"].encode("utf-8")
    record = json.loads(record_bytes)
    reference = record["record_digest_ref"]
    if not re.fullmatch(r"receipt-[1-9][0-9]*", reference):
        issue("FAIL", "RECEIPT_REFERENCE_NOT_DETACHED")
        return
    receipt = example.get("receipt")
    if receipt is None:
        issue("BLOCKED", "RECEIPT_MISSING")
        return
    record_id = record["record_id"]
    if receipt.get("id") != reference or receipt.get("record_id") != record_id or records_by_id.get(record_id) != record:
        issue("FAIL", "RECEIPT_BINDING_MISMATCH")
    if receipt.get("sha256") != hashlib.sha256(record_bytes).hexdigest():
        issue("FAIL", "RECORD_DIGEST_MISMATCH")


def aggregate(statuses):
    return min(statuses, key=SEVERITY.__getitem__, default="PASS")


def evaluate(fixture):
    if fixture["kind"] != "stage0-synthetic" or not fixture["records"]:
        raise ValueError("A nonempty Stage 0 synthetic record set is required")
    reasons = {}

    def issue(status, reason):
        reasons[reason] = status

    classifications = {}
    by_execution = {}
    records_by_id = {}
    records = fixture["records"]
    for record in records:
        record_id, execution = record["record_id"], record["execution_id"]
        if not all(nonblank(record[key]) for key in (
            "record_id", "task_id", "attempt_id", "execution_id", "repository"
        )):
            issue("FAIL", "IDENTIFIER_MISSING")
        if record_id in records_by_id:
            issue("FAIL", "DUPLICATE_RECORD_ID")
        if execution in by_execution:
            issue("FAIL", "DUPLICATE_EXECUTION_ID")
        records_by_id[record_id] = record
        by_execution[execution] = record
        evidence = fixture["evidence"].get(record_id, {})
        if evidence and any(evidence.get(key) != record[key] for key in ("repository", "commit", "tree", "execution_id")):
            issue("FAIL", "EVIDENCE_TARGET_MISMATCH")
        classifications[record_id] = observed_class(record, evidence, issue)

    check_history(records, fixture.get("prior_records", []), issue)
    check_delegation(fixture, by_execution, issue)
    audit_status = check_audit(fixture.get("audit"), fixture.get("audit_evidence", {}), records_by_id, issue)
    check_receipt(fixture.get("receipt_check"), records_by_id, issue)
    return {
        "classifications": classifications,
        "input_status": aggregate(reasons.values()),
        "reason_codes": sorted(reasons),
        "audit_status": audit_status,
        "permit": {"A": False, "B": False, "C": False},
    }


if __name__ == "__main__":
    path, case_id, variant = sys.argv[1:]
    cases = json.loads(Path(path).read_text(encoding="utf-8"))
    print(json.dumps(evaluate(cases[case_id][variant]), sort_keys=True))
