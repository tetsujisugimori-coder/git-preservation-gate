# Issue #14 Level 1 default-input contract

Scope: synthetic trusted-record validation only. This does not authorize actual storage, create approvals, change the adopted central v0.2.0 policy, or grant production permission. Issue #13 remains an unadopted future revision proposal.

## Level 1 default behavior
Ordinary public, retrievable Git code and documentation need no extra Archive inputs. The compact path of tools/stage1b/contract.py accepts a smaller record: schema_version, repository, ref, head, tree, parents, object id/kind=git-document, level=1, policy version/commit, risk rationale/flags and observations. No approval_id, destination, retention_until, ACL, actor, operations, audit mode or archive session fields are required. Missing ci_required defaults to true, never a waiver. Missing CI/review/permissions observations default to NOT_TESTED, not PASS. Required failure or HEAD mismatch still rejects acceptance.

The compact risk record requires five boolean fields: confidential, destructive, strong_authenticity, important_evidence, publicly_retrievable, plus a nonempty rationale. None of these booleans silently default. Any of the first four risks being true, or publicly_retrievable=false, rejects Level 1. The caller must check the actual file type, sensitivity, reproducibility, permissions and classification independently. The validator does not authenticate self-reported risk or source control authority.

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
The alternative requested_by value is case_contract. Required additional save fields are attempt_id, approval_id, destination, operations, actor, classification, retention_until, audit_mode, and object.size/object.sha256, plus an independently verified approval record. Incomplete additional inputs block only archive_status, not the unrelated Git acceptance. Malformed request metadata has the same separation. Known archive content/custody failures are retained even when metadata is missing.

The adapter internally reuses the existing strict Stage 1-B approval/scope checker, with Level 2 mechanics for that archive operation only. The declared original Git artifact remains Level 1. No external authorization is inferred. Archive verification of non-bundle Git documents requires readback, size, SHA-256 and all bytes, not bundle restore. Incomplete evidence and independently unverified scope never become real PASS. production_permit remains false.

Existing complete schema v1 records, including historical Level 1 fixtures, remain on the original code path. Level 2 and Level 3 paths are unchanged. The Issue #13 proposed owner-specified Level 3 semantics are not implemented.

## User experience
PC and mobile forms and CLI entry points should expose only normal Git identity/risk and CI/review/permission checks by default. Storage/ACL/retention fields appear only on deliberate additional-save opt-in. No implicit disk write, retention assurance, directory creation or ACL modification is permitted.

## Verification
- New independent synthetic counterexamples: tests/stage1b/test_level1_defaults.py (35 cases).
- CI: .github/workflows/issue14-level1-defaults.yml. Re-runs prior Stage 1-B oracle/overlay, P2/review and Stage1A/B2 regressions, and existing Windows bounded 21 cases.
- Synthetic CI cannot prove real storage, third-party independence, Windows write scope or production deployment.
- Before merge, independent reviewer must fetch final HEAD, inspect diff and re-run with additional adversarial cases. Keep Draft and preserve old evidence and failed runs.
