# Stage 1-B storage-contract validation module

**Issue #14 status (2026-11-19 JST): PARTIAL.** Compact Level 1 synthetic self-checks are complete. The fixed Draft PR awaits independent review. Limited technical acceptance and limited merge recommendation are NO. [Issue #14 specification and verification scope](../../docs/stage1b/issue14-level1-defaults.md)

This pure module validates **trusted input records**, not the identity/authority of an owner, authenticity of evidence, ACL enforcement, or storage durability. `production_permit` is always false. A syntactically valid approval or receipt is not proof that approval/storage occurred. Actual operations require independently established authority and an implementation-specific safety gate.

## Input contract (schema version 1)
`validate_contract(contract, approval, now, observed_head)` takes JSON-compatible dictionaries. Exact key/type validation is implemented in `schema` and `approval_schema`; unknown keys, bool-as-int, duplicate arrays, naive timestamps, malformed hashes and empty identity fields are rejected.

The complete fixture is `tests/stage1b/contract_cases.json` C01. Required identities: repository/ref/head/tree/parents; object id/size/SHA256/kind; attempt; policy version+commit; Level and confidentiality/destruction/authenticity rationale; approval id; destination/operation/actor/classification; retention and prohibition of deletion/move/overwrite; audit mode; basic and additional checks; observed states; separate execution/session/area/retrieval conditions.

Approval input fixes case or reusable scope, repositories/object IDs/classifications/destinations/actors/operations, validity interval, retention, destruction policy, ACL observation and independently checked authorization boolean. `authorization_verified=true` is a trusted caller assertion, not authentication performed by this module. IDs and policy commit must be bound to external reviewed records by the caller. The module does not discover approval records, authorize network transfers, or certify that a policy commit is the currently adopted version. Scope reuse matches explicit lists; no wildcard expansion. Case scope has one repo and one object ID. Object ID bindings require external canonical identity records; receipt matching additionally checks contract SHA and size.

Level 1 git-document does not require an Archive approval or storage check. Evidence/bundle/ZIP needs at least Level 2; special risk needs Level 3. Level 2 basic content checks cannot be omitted. Bundles require restore; ZIPs require CRC, safe paths and manifest checks, not imposed on non-ZIP. Level 3 extra decision must be explicitly approved with rationale; required extra checks are declared but their execution adapter is NOT_TESTED, so acceptance stays BLOCKED when additional checks are required. No universal VM/account requirement is imposed.

## Separate results
`contract_status` describes schema/scope eligibility only. It can PASS while storage remains NOT_TESTED or FAIL. CUSTODY is the observed storage state; VERIFICATION aggregates direct readback/content/restore observations. INDEPENDENCE records separate session/execution/area/direct retrieval; SOLO may be technically sufficient with PARTIAL and human label LIMITED_SHARED_OWNER, never third-party human PASS. STRICT additionally requires human separation. ACCEPTANCE requires applicable checks and review/CI, while production permission remains false even if these trusted records agree.

Known storage/content FAIL survives classification and other contract errors. A malformed contract never becomes operationally valid merely because one evidence axis is PASS. A later correct attempt appends results; it does not rewrite failed attempts.

## Receipt/manifest and attempts
`validate_manifest` checks nonempty file list, unique safe relative paths, size and SHA-256. It is a structural check, not a filesystem hash computation. `validate_receipt` matches attempt/object/destination/SHA/size and records separate storage/readback status. A failed or custody-only receipt is valid evidence of failure/incompleteness, not preservation PASS.

`claim_attempt(existing_ledger, id)` uses create-exclusive reservation of a new JSON file with state PENDING. Existing claims, including interrupted work, are rejected; the helper never removes or overwrites them. Recovery requires a new attempt ID referring to prior evidence. This local helper is not a hostile-filesystem sandbox or cross-machine transaction service.

## Tests
28 oracle-fixed contract cases plus 16 record/attempt cases. Original oracle SHA is in `oracle-fixed.json`; initial run had four axis-preservation mismatches, retained in evidence. Implementation was corrected to preserve separately typed observations without changing those expectations. Final run reports checker/oracle/input SHA, expected/actual status axes and timestamps. stdout JSON and stderr are stored separately. Synthetic trusted-input tests do not validate actual approval authority, Windows storage, persistence, or real evidence integrity.

Commands (run with an outer 20-second deadline; no retry):
```
python tests/stage1b/run_contract_tests.py
python tests/stage1b/run_record_tests.py <new-test-ledger>
```
The second command requires a nonexistent ledger; it leaves the new reservation in place. Stage 1-A files and evidence are unchanged.

## Boundary correction, independent of initial oracle
`validate_contract(..., effective_policy=...)` now requires a trusted adopted policy descriptor for contract PASS. Missing confirmation is UNKNOWN; mismatch is FAIL. Tests pass an explicitly synthetic fixed descriptor, never a claim that its hash identifies a real adopted policy. The real caller must read adopted policy and pass its verified version/commit.

ZIP execution adapters are not implemented here. Even with base observations all PASS and required ZIP checks declared, VERIFICATION is NOT_TESTED and ACCEPTANCE BLOCKED (known hash FAIL remains FAIL). Unknown check adapters similarly prevent acceptance. Six added pre-fixed cases verify these boundaries; the pre-fix ZIP false acceptance is retained. No old oracle was changed.

## Independent review corrections
Risk-specific L3 approval must explicitly list every active `confidential`, `destructive`, `strong_authenticity` flag in `extra_decision.covered_risks`; omission is UNKNOWN, not an implicit waiver. A generic old 'no special risk' assertion cannot waive newly active risks. Both approved and requested retention must extend beyond the evaluation timestamp. An unknown shared-owner state does not yield INDEPENDENCE PASS. Initial review counterexamples are preserved and rerun unchanged. These are trusted-record consistency checks, not external approval authentication.

## P2-01 to P2-03 v0.2.0 review amendment
Frozen 28-case historical oracle remains unchanged. Corrections are explicitly overlaid by `tests/stage1b/oracle-v020-p2.json` with old expected values also retained by the runner; C16's missing L3 decision is added to verification. The 18 new preregistered synthetic regression cases are `tests/stage1b/run_p2_regression.py`.

P2-01: FAIL takes precedence, then BLOCKED, then one kind of incomplete state, else mixed PARTIAL. An incomplete required CI/review/readback without an actual blocker gives acceptance PARTIAL. Real blockers (scope/approval uncertainty, missing audit separation) remain BLOCKED. Known content failure remains FAIL.

P2-02: `extra_decision.approved=false` without optional `approval_state` denotes explicit denial (FAIL), never UNKNOWN. Optional `approval_state` is PASS/FAIL/UNKNOWN/NOT_TESTED and must agree with the legacy boolean. Those states contribute to the extra contract and verification; actual approval authentication is still outside the module.

P2-03: A false `ci_required` requires `ci_exemption` with nonempty rationale, exact repository/ref/head/object_id. Missing or mismatched waiver is BLOCKED; invalid structure/schema fails. A waiver cannot coexist with `ci_required=true`. Waiving CI never changes the CI observation to PASS.

This development-stage amendment does not authenticate external approval, save anything to a durable destination, claim an independent human audit or enable production permit.

## Issue #14 compact Level 1 input (separate follow-up, synthetic only)
A compact opt-in path accepts regular public/retrievable Git documents without any archive-specific fields. Missing ci_required defaults to true. Risk flags and a classification rationale are required; needed CI/review/permissions observations are never manufactured as PASS. The initial Git-only path returns archive_applicability.required=false, and CUSTODY/VERIFICATION/INDEPENDENCE remain NOT_TESTED. An explicit archive_request triggers a separate archive_status; missing scope/destination/retention/authorization stops only the archive action. Actual save operations are not executed here. The previous full-schema Level 1 records, Level 2/3 and historical fixtures remain on the legacy path.

Specification and examples: ../../docs/stage1b/issue14-level1-defaults.md
New synthetic tests: ../../tests/stage1b/test_level1_defaults.py
