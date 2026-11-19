# Issue #14 Level 1 default-input contract

**Current decision (2026-11-19 JST): PARTIAL.** Implementation and synthetic self-checks are complete. Limited technical acceptance and limited merge recommendation are **NO** pending fixed-version independent review. `production_permit=false`. [Draft PR #19 records the published commit, tree, parent, and formal CI](https://github.com/tetsujisugimori-coder/git-preservation-gate/pull/19).

Scope: synthetic trusted-record validation only. This does not authorize actual storage, create approvals, change the adopted central v0.2.0 policy, or grant production permission. Issue #13 remains an unadopted future revision proposal.

## Level 1 default behavior
Ordinary public, retrievable Git code and documentation need no extra Archive inputs. The compact path of tools/stage1b/contract.py accepts a smaller record: schema_version, repository, ref, head, tree, parents, object id/kind=git-document, level=1, policy version/commit, risk rationale/flags and observations. No approval_id, destination, retention_until, ACL, actor, operations, audit mode or archive session fields are required. Missing ci_required defaults to true, never a waiver. Missing CI/review/permissions observations default to NOT_TESTED, not PASS. Required failure or HEAD mismatch still rejects acceptance.

The compact risk record requires five boolean fields: confidential, destructive, strong_authenticity, important_evidence, publicly_retrievable, plus a nonempty rationale. Any of the first four risks being true, or publicly_retrievable=false, rejects Level 1 and rules out its Archive exemption. An explicit Archive request on an underclassified record also fails. The caller must check the actual file type, sensitivity, reproducibility, permissions and classification independently. The validator does not authenticate self-reported risk or source control authority.

Example synthetic contract (the hashes are test placeholders, not real verified HEADs):

~~~json
{
  "schema_version": "1",
  "repository": "example/repo",
  "ref": "refs/heads/topic",
  "head": "1111111111111111111111111111111111111111",
  "tree": "2222222222222222222222222222222222222222",
  "parents": ["3333333333333333333333333333333333333333"],
  "object": {"id": "docs/guide.md", "kind": "git-document"},
  "level": 1,
  "risk": {
    "confidential": false,
    "destructive": false,
    "strong_authenticity": false,
    "important_evidence": false,
    "publicly_retrievable": true,
    "rationale": "Public, retrievable normal Git document, source checked externally"
  },
  "policy": {"version": "0.2.0", "commit": "4444444444444444444444444444444444444444"},
  "observations": {"ci": "PASS", "review": "PASS", "permissions": "PASS"}
}
~~~

Default output: archive_applicability.required=false; archive status and CUSTODY/VERIFICATION/INDEPENDENCE statuses all NOT_TESTED. These are not synthetic success statuses. A trusted caller must independently supply observations of CI, review and permissions. Absence of required observations is incomplete, not approved.

## Explicit additional save
The additional-archive request must be explicitly supplied as:
~~~json
{"archive_request":{"requested_by":"owner","reason":"Case-scoped extra archive"}}
~~~
The alternative requested_by value is case_contract. Required additional save fields are attempt_id, approval_id, destination, operations, actor, classification, retention_until, audit_mode, and object.size/object.sha256, plus a trusted approval record. The approval includes a destination ACL observation (`acl`) and independently verified authorization. Reusable approval is eligible when it covers the repository, object, classification, destination, actor, operations, retention and evaluation time. Incomplete or malformed archive inputs block the archive while Git acceptance uses its own evidence. An observed storage, readback, size, SHA-256 or byte comparison failure keeps the relevant axis and archive outcome at FAIL even when other archive inputs are missing or malformed.

The adapter reuses the Stage 1-B approval/scope checker for that archive operation. Archive verification of Git documents requires readback, size, SHA-256 and all bytes. An explicitly required check unavailable for this path blocks the archive with verification NOT_TESTED unless a content failure is already known. The results evaluate trusted records. Production permission requires separate authority and remains false here.

Existing complete schema v1 records, including historical Level 1 fixtures, remain on the original code path. Level 2 and Level 3 paths are unchanged. The Issue #13 proposed owner-specified Level 3 semantics are not implemented.

## Python API and future PC/mobile integration
The current input entry point is the Python function `validate_contract` in `tools/stage1b/contract.py`. Both package imports (`from tools.stage1b.contract import validate_contract`) and existing callers importing `contract` directly are supported. The repository provides command-line test runners and synthetic adapters. A user-facing Level 1 CLI, PC/mobile form and HTTP endpoint are pending.

An integration should resolve the named repository and ref, bind the object, tree and parents to that commit, and refresh the observed HEAD before acceptance. Pass the verified value as `observed_head` and the adopted policy as `effective_policy`. Supply observations for the same revision and operation from the relevant CI, review and permissions sources. Leave evidence absent or `NOT_TESTED` until observed. Use the compact shape for new Level 1 entries. The full historical shape keeps its original observation contract.

Show the Git identity, classification and applicable gate observations in the normal PC/mobile workflow. Surface the archive fields and approval lookup only after an owner or case-contract request. Display `ACCEPTANCE_STATUS` for the Git decision and `archive_status` with its reasons for the archive decision. The evaluator operates in memory. Any future save adapter needs its own authorization and execution gate.

## Verification
- Level 1 synthetic self-checks in `tests/stage1b/test_level1_defaults.py`: 54/54, including the original 35. A pre-fix run with the first 14 additions had nine mismatches. The original 35 cases matched in that run.
- The original 131-case set covers contract/record/boundary (50 with the documented overlays), prior reviewer fixtures (10), P2 (18), Stage 1-A (32), and Windows finite-stop (21). Review fixtures (13 and 17) and publication checks (10) are additional. The 21 Windows cases are repeated under Windows PowerShell 5.1 and PowerShell 7 in the Issue #14 workflow.
- The normal-user Windows Stage 1-B2 run matched 42/43, with B230 NOT_TESTED due to unavailable link creation. Its 11 report-validation tests passed. The formal Linux run is recorded separately in the PR.
- Synthetic CI cannot prove real storage, third-party independence, Windows write scope or production deployment.
- Before merge, independent reviewer must fetch final HEAD, inspect diff and re-run with additional adversarial cases. Keep Draft and preserve old evidence and failed runs.
