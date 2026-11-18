# PR #6 P2 independent re-review

## Scope and identity
Separate AI reviewer B retrieved local commit `f94bfc42c19bc2c4d36bb7d2fefd56db113e8622` into a separate clone with no hardlinks. This is separate responsibility/session, not separate human, account, infrastructure, or filesystem ownership. Production storage, genuine approval, risk completeness and actual preservation are NOT_TESTED.

## Fixed expectations and retained history
The new 32-case oracle was fixed before repaired-checker execution. Original 49 inputs and old expectations remain unchanged. A separate reassessment overlay changes V019 because an absent Level 3 contract cannot establish verification. The first overlay accidentally omitted V041; after implementer self-test surfaced this, reviewer B corrected that omission under the already fixed missing-contract rule. Both overlays and the correction note remain. Thus expectations were not all immutable from the first attempt; the precisely bounded correction is disclosed. Old expectation comparison is 47/49, not falsely 49/49.

## Findings and verification
P2-01 CLOSED in synthetic design scope: an empty additional list is not evidence of an approved no-extra decision. Each known Level 3 risk requires an explicit contract, rationale, scope and approval observation. Missing contract/unknown remains UNKNOWN; unexecuted remains NOT_TESTED; failures remain FAIL. Approved baseline-only cases for confidentiality, irrecoverability, destructive operations and strong authenticity are allowed without arbitrary extra checks.

P2-02 CLOSED in synthetic design scope: too-low classification no longer hides known SHA, storage or required-CI failures. Other unresolved axes stay UNKNOWN. All hypothetical eligibility is false on invalid classification; actual permit is always false.

An additional P2 boundary found by B showed new risk-contract approval FAIL masked by uncertain classification. Three new cases were fixed before execution, all reproduced the defect, and the same three pass after repair. No expectation relaxation.

Independent results: new32/32, original49 reassessment49/49, extra3/3, schema29/29, runner4/4, legacy AT52/52. Old AT implementation/fixtures/oracle remain fixed; these are not new preservation operations. Runner preflight faults exit2 with NOT_TESTED and no checker runs. Full stdout/stderr/exit, timing, input/checker hashes and timeout/retry are retained in logs.

## Verdict
Remaining P1/P2/P3: 0 in the reviewed change scope. Stage 0 design/synthetic limited acceptance YES; limited merge recommendation YES subject to final submitted-byte readback. Formal adoption PENDING, Stage 1 NO, other-repository forced application NO. No merge or real storage authorization is issued.

## Final submission
GitHub fixed-HEAD readback is a separate pending step at creation of this report. It must establish that reviewed source, fixtures and this report match the final submitted version. This report is not permanent-custody evidence.

## Final-document and newly introduced runner review
The subsequent document/log snapshot a59fe840fe3eae945f93adfaf55fc59129af1c6e is consistent with the reviewed checker and fixtures. An additional P2 was discovered in its new convenience runner: empty and duplicate fixture inventories exited successfully, and missing expected fields raised an exception without an outcome log. This is not covered by the older runner's four tests. Three new expectations were fixed before execution and reproduced all three problems.

The repaired runner at e8f0375 was obtained from the repository object and its bytes match the executed snapshot. The same three faults now exit2, NOT_TESTED, zero checker rows. A normal 32-case run is 32/32. Separately predeclared invalid checker stdout is retained and classified FAIL with exit1, rather than losing the record. These are 3 fault cases + 1 output-failure case for the new runner, additional to the old four. The additional P2 is CLOSED.

All earlier checker/oracle hashes remain unchanged. The unpublished fixture-builder remains locally preserved and is not a supported reproduction command. Final GitHub submitted-byte readback remains a distinct step; no policy adoption or production operation is authorized.
