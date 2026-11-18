"""Stage 1-B P2-01..03 pre-fixed counterexamples. Synthetic; never a permit."""
import copy
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "stage1b"))
from contract import aggregate, validate_contract

FIX = json.loads((ROOT / "tests/stage1b/contract_cases.json").read_text(encoding="utf-8"))
BASE = FIX["cases"][0]["input"]
POLICY = {"version": "0.2.0", "commit": "4" * 40}


def trial():
    x = copy.deepcopy(BASE)
    c = x["contract"]
    c["observations"] = {k: "PASS" for k in c["observations"]}
    c["sessions"].update(separate_session=True, separate_execution=True,
                         separate_area=True, direct_retrieval=True, shared_owner=True)
    return x


def ci_exception(c):
    c["ci_required"] = False
    c["ci_exemption"] = {
        "rationale": "Synthetic fixture with no required CI for this exact object",
        "repository": c["repository"], "ref": c["ref"],
        "head": c["head"], "object_id": c["object"]["id"],
    }


def level3(c, approval):
    c["level"] = 3
    c["risk"]["confidential"] = True
    c["extra_decision"] = {
        "decision": "not_required",
        "rationale": "Basic checks sufficient for synthetic confidential case",
        "approved": approval,
        "covered_risks": ["confidential"],
    }


cases = []

def check(name, data, expected):
    c = data["contract"]
    actual = validate_contract(c, data["approval"], data["now"],
                               data["observed_head"], POLICY)
    mismatches = {key: {"expected": value, "actual": actual.get(key)}
                  for key, value in expected.items() if actual.get(key) != value}
    cases.append({"id": name, "match": not mismatches, "mismatches": mismatches,
                  "production_permit": actual.get("production_permit")})


x = trial()
x["contract"]["observations"]["readback"] = "NOT_TESTED"
check("P201-storage-pass-readback-not-tested", x,
      {"VERIFICATION_STATUS": "NOT_TESTED", "ACCEPTANCE_STATUS": "PARTIAL"})
x = trial()
x["contract"]["observations"]["ci"] = "NOT_TESTED"
check("P201-required-ci-not-tested", x, {"ACCEPTANCE_STATUS": "PARTIAL"})
x = trial()
x["contract"]["observations"]["review"] = "UNKNOWN"
check("P201-review-unknown", x, {"ACCEPTANCE_STATUS": "PARTIAL"})
x = trial()
x["contract"]["observations"]["sha256"] = "FAIL"
x["contract"]["observations"]["readback"] = "NOT_TESTED"
check("P201-known-hash-fail-dominates", x,
      {"VERIFICATION_STATUS": "FAIL", "ACCEPTANCE_STATUS": "FAIL"})
x = trial()
x["approval"] = None
check("P201-missing-approval-blocks", x,
      {"contract_status": "BLOCKED", "ACCEPTANCE_STATUS": "BLOCKED"})

x = trial()
level3(x["contract"], False)
check("P202-explicit-denial", x,
      {"contract_status": "FAIL", "VERIFICATION_STATUS": "FAIL",
       "ACCEPTANCE_STATUS": "FAIL"})
x = trial()
level3(x["contract"], False)
x["contract"]["extra_decision"]["approval_state"] = "UNKNOWN"
check("P202-approval-unknown", x,
      {"contract_status": "UNKNOWN", "VERIFICATION_STATUS": "UNKNOWN",
       "ACCEPTANCE_STATUS": "BLOCKED"})
x = trial()
level3(x["contract"], False)
x["contract"]["extra_decision"]["approval_state"] = "NOT_TESTED"
check("P202-approval-not-tested", x,
      {"contract_status": "NOT_TESTED", "VERIFICATION_STATUS": "NOT_TESTED",
       "ACCEPTANCE_STATUS": "PARTIAL"})
x = trial()
level3(x["contract"], True)
check("P202-approved-basic-sufficient", x, {"ACCEPTANCE_STATUS": "PASS"})
x = trial()
level3(x["contract"], True)
x["contract"]["extra_decision"]["approval_state"] = "FAIL"
check("P202-contradictory-approval-schema", x,
      {"contract_status": "FAIL", "ACCEPTANCE_STATUS": "FAIL"})

x = trial()
x["contract"]["ci_required"] = False
check("P203-exemption-without-basis", x,
      {"contract_status": "BLOCKED", "ACCEPTANCE_STATUS": "BLOCKED"})
x = trial()
ci_exception(x["contract"])
x["contract"]["ci_exemption"]["head"] = "0" * 40
check("P203-exemption-wrong-head", x,
      {"contract_status": "BLOCKED", "ACCEPTANCE_STATUS": "BLOCKED"})
x = trial()
ci_exception(x["contract"])
x["contract"]["ci_exemption"]["rationale"] = ""
check("P203-exemption-empty-rationale", x,
      {"contract_status": "FAIL", "ACCEPTANCE_STATUS": "FAIL"})
x = trial()
ci_exception(x["contract"])
x["contract"]["observations"]["ci"] = "NOT_TESTED"
check("P203-scoped-exemption-ci-not-tested", x,
      {"contract_status": "PASS", "ACCEPTANCE_STATUS": "PASS"})
x = trial()
ci_exception(x["contract"])
x["contract"]["ci_required"] = True
check("P203-ci-required-waiver-conflict", x,
      {"contract_status": "FAIL", "ACCEPTANCE_STATUS": "FAIL"})

aggregation = [
    ("P201-unknown-plus-not-tested", ["UNKNOWN", "NOT_TESTED"], "PARTIAL"),
    ("P201-pass-plus-not-tested", ["PASS", "NOT_TESTED"], "NOT_TESTED"),
    ("P201-fail-plus-blocked", ["FAIL", "BLOCKED"], "FAIL"),
]
for name, values, expected in aggregation:
    actual = aggregate(values)
    cases.append({"id": name, "match": actual == expected,
                  "expected": expected, "actual": actual, "production_permit": False})

passed = sum(c["match"] and c["production_permit"] is False for c in cases)
report = {"suite": "stage1b-new-p2-pre-fixed", "passed": passed,
          "total": len(cases), "cases": cases,
          "scope": "pure synthetic contract, no actual permission or save"}
print(json.dumps(report, ensure_ascii=False, indent=2))
sys.exit(0 if passed == len(cases) else 1)
