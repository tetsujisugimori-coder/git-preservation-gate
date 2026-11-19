"""Issue14 independent adversarial operation-boundary counterexamples.

This is a pure trusted-input test. PASS of old code for read-only is the
pre-fix defect witness, not evidence of a real save or approval.
"""
import argparse
import copy
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/stage1b"))
from contract import validate_contract

P = argparse.ArgumentParser()
P.add_argument("--baseline-only", action="store_true")
args = P.parse_args()
HEAD = "1" * 40
POLICY = {"version": "0.2.0", "commit": "4" * 40}
NOW = "2026-11-19T00:00:00+00:00"
END = "2027-01-01T00:00:00+00:00"

def template():
    c = {
        "schema_version": "1",
        "repository": "example/independent-operation-test",
        "ref": "refs/heads/fixture",
        "head": HEAD,
        "tree": "2" * 40,
        "parents": ["3" * 40],
        "object": {"id": "docs/guide.md", "kind": "git-document",
                   "size": 200, "sha256": "a" * 64},
        "level": 1,
        "risk": {"confidential": False, "destructive": False,
                 "strong_authenticity": False, "important_evidence": False,
                 "publicly_retrievable": True,
                 "rationale": "Synthetic public retrievable Git document"},
        "policy": POLICY.copy(),
        "observations": {"ci": "PASS", "review": "PASS",
                         "permissions": "PASS", "storage": "PASS",
                         "readback": "PASS", "size": "PASS",
                         "sha256": "PASS", "all_bytes": "PASS"},
        "archive_request": {"requested_by": "owner",
                            "reason": "Synthetic new archive save and verification"},
        "attempt_id": "independent-new-save",
        "approval_id": "SYNTHETIC-APPROVAL",
        "destination": "synthetic-destination",
        "operations": ["create", "read"],
        "actor": "synthetic-owner",
        "classification": "public",
        "retention_until": END,
        "audit_mode": "SOLO_STANDARD",
        "sessions": {"separate_session": True,
                     "separate_execution": True,
                     "separate_area": True,
                     "direct_retrieval": True,
                     "human_independent": None,
                     "shared_owner": True},
    }
    approval = {
        "id": "SYNTHETIC-APPROVAL",
        "scope": "case",
        "repositories": ["example/independent-operation-test"],
        "object_ids": ["docs/guide.md"],
        "classifications": ["public"],
        "destinations": ["synthetic-destination"],
        "actors": ["synthetic-owner"],
        "operations": ["create", "read"],
        "valid_from": "2026-01-01T00:00:00+00:00",
        "valid_until": END,
        "retention_until": END,
        "delete_move_overwrite": "prohibited",
        "acl": "PASS",
        "authorization_verified": True,
    }
    return c, approval

def case(operations, *, observed_fail=None, approved_operations=None):
    contract, approval = template()
    contract["operations"] = operations
    approval["operations"] = (approved_operations if approved_operations is not None
                                else operations)
    if observed_fail:
        contract["observations"][observed_fail] = "FAIL"
    return validate_contract(contract, approval, NOW, HEAD, POLICY)

witness = case(["read"])
if args.baseline_only:
    success = witness["ACCEPTANCE_STATUS"] == "PASS" and witness["archive_status"] == "PASS"
    print(json.dumps({"scope": "pre-fix code-only synthetic defect witness",
                      "case": "read-only-authorized-but-new-save-reported-PASS",
                      "observed": witness,
                      "defect_reproduced": success, "production_permit": False}, indent=2))
    sys.exit(0 if success else 1)

checks = []
def check(name, result, expected):
    wrong = {key: {"expected": value, "actual": result.get(key)}
             for key, value in expected.items() if result.get(key) != value}
    checks.append({"id": name, "verdict": "PASS" if not wrong else "FAIL",
                   "mismatch": wrong, "actual": result})
    if result.get("production_permit") is not False:
        checks[-1]["verdict"] = "FAIL"
        checks[-1]["mismatch"]["production_permit"] = result.get("production_permit")

check("IO-01-read-only-is-not-a-new-save", witness,
      {"ACCEPTANCE_STATUS": "PASS", "archive_status": "BLOCKED",
       "archive_create_status": "NOT_TESTED", "archive_readback_status": "PASS"})
check("IO-02-create-only-is-not-verified-save", case(["create"]),
      {"ACCEPTANCE_STATUS": "PASS", "archive_status": "BLOCKED",
       "archive_readback_status": "NOT_TESTED"})
check("IO-03-create-and-read-accepted-synthetic", case(["create", "read"]),
      {"ACCEPTANCE_STATUS": "PASS", "archive_status": "PASS",
       "archive_create_status": "PASS", "archive_readback_status": "PASS"})
check("IO-04-read-only-known-SHA-failure-persists", case(["read"], observed_fail="sha256"),
      {"ACCEPTANCE_STATUS": "PASS", "archive_status": "FAIL",
       "VERIFICATION_STATUS": "FAIL", "archive_create_status": "NOT_TESTED"})
check("IO-05-read-only-known-storage-failure-persists", case(["read"], observed_fail="storage"),
      {"ACCEPTANCE_STATUS": "PASS", "archive_status": "FAIL",
       "CUSTODY_STATUS": "FAIL", "archive_create_status": "NOT_TESTED"})
check("IO-06-created-but-read-not-authorized", case(["create"], approved_operations=["create"]),
      {"archive_status": "BLOCKED", "archive_readback_status": "NOT_TESTED"})
check("IO-07-both-operations-requested-but-approval-read-only",
      case(["create", "read"], approved_operations=["read"]),
      {"archive_status": "BLOCKED", "archive_contract_status": "BLOCKED"})
c8, a8 = template()
c8["observations"]["storage"] = "NOT_TESTED"
check("IO-08-unobserved-create-cannot-be-PASS",
      validate_contract(c8, a8, NOW, HEAD, POLICY),
      {"archive_status": "PARTIAL", "archive_create_status": "NOT_TESTED"})

# P3: distinguish incomplete request, malformed approval schema, and known FAIL.
c9, a9 = template()
a9.pop("acl")
check("IO-09-missing-approval-acl-is-BLOCKED",
      validate_contract(c9, a9, NOW, HEAD, POLICY),
      {"ACCEPTANCE_STATUS": "PASS", "archive_status": "BLOCKED",
       "archive_contract_status": "BLOCKED"})
c10, a10 = template()
a10["acl"] = "INVALID_STATE"
check("IO-10-malformed-approval-acl-schema-is-FAIL",
      validate_contract(c10, a10, NOW, HEAD, POLICY),
      {"ACCEPTANCE_STATUS": "PASS", "archive_status": "FAIL",
       "archive_contract_status": "FAIL"})
c11, a11 = template()
c11["archive_request"].pop("reason")
check("IO-11-malformed-archive-request-is-BLOCKED",
      validate_contract(c11, a11, NOW, HEAD, POLICY),
      {"ACCEPTANCE_STATUS": "PASS", "archive_status": "BLOCKED",
       "archive_contract_status": "BLOCKED"})

failures = [item["id"] for item in checks if item["verdict"] != "PASS"]
print(json.dumps({"suite": "issue14-independent-operation-boundary",
                  "total": len(checks), "passed": len(checks)-len(failures),
                  "failures": failures, "cases": checks,
                  "production_permit": False}, indent=2))
sys.exit(1 if failures else 0)
