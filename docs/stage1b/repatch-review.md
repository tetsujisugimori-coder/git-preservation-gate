# Stage 1-B P2-B01/B02 re-correction

2026-11-18. Existing Issue #11 / Draft PR #12; starting HEAD
`c52194dc7d290e409d8f7b60ab5015aa81a05969`, tree
`73876cfb7368fe1e86cdc02e5c220e0c4f392d27`, base/main
`4695c3ce2d61e66df0dd36a4312373459e1557d4`.
No AGENTS.md in the starting Git tree. Policy and audit contracts at this base are formally adopted v0.2.0 and are unchanged.

## Current acceptance
Overall PARTIAL; implementation self-checks complete; independent fixed-submission review, current CI and normal Windows repeats pending. Limited acceptance/merge recommendation NO until these complete. Production permit remains false; real durable storage and Stage 1-C are not accepted. Historical YES and CI-zero reports elsewhere describe earlier versions, not this decision.

## Changes and explicit contracts
- P2-B01: `archive_applicability` explicitly records required bool and reason. A legitimate L1 Git document has non-applicable custody/verification/independence NOT_TESTED, not PASS. Raw `archive_observations` retain observations without treating optional archive checks as required Git acceptance. HEAD/policy/schema/required CI/review still apply. A falsely low declaration of a high-risk or important-evidence object is not this exemption. L2/L3 mandatory failures remain.
- P2-B02: schema rejects unknown, duplicate, and non-active covered risks separately. Missing active risks remain incomplete contract UNKNOWN / blocked acceptance, in accordance with adopted audit contract. The active risk set and classification policy are not redefined. No acceptance of real approval authenticity is inferred.
- P3-B03: known shared owner in STRICT is BLOCKED even when human_independent=true is asserted. SOLO's same-owner technical audit remains possible. Unknown owner stays UNKNOWN.
- P3-B04: current version/pending decision is added ahead of historical result/review/README text; prior reports are not deleted.
- Pre-publication scanner recursively checks keys/values and bounded escaped separator/unicode decoding. It returns no matched private string. Ten synthetic tests cover clean/nested/key/double JSON/unicode/slash/UNC/hex inputs and two safe-display false-positive controls. This is a conservative path pattern detector, not comprehensive secret detection or historical erasure. Historical unreferenced-blob P3 remains OPEN and old cloud raw retention UNKNOWN.

## Fixed oracles and RED/GREEN
Original independent 12 cases and NEW13 were copied byte-identically from the prior review evidence. SHA identifiers are recorded. Original inputs and expectations are never edited. Baseline checker is obtained using Git show at the starting commit and run against those same inputs: 9/13 match (exit1), new checker 13/13 (exit0).

Additional 17 boundary expectations are separately frozen before their execution: L1 required CI/review/HEAD, optional observations, L2 separation/SHA, L3 exact/missing/unknown/duplicate risks and approval states, STRICT known/unknown/separate owner. These are synthetic contract tests, not operational permission.

Existing 50 tests initially yielded 48 matches after correction. Two intentional expectation differences follow directly from the requested policy correction: C26 known shared STRICT owner now BLOCKED rather than UNKNOWN/PARTIAL; C27 L1 non-applicable independence now NOT_TESTED rather than UNKNOWN. The original fixture and prior overlay remain unchanged, the failing transcript is retained, and `oracle-repatch-overlay.json` separately states the reason and new expectations. All 50 then match. The original 10, P2 18 and Stage1A 32 remain unchanged.

## Evidence and limits
New evidence is in `evidence/stage1b-repatch/`, separate from the original evidence manifest. Source/runner/oracle SHA, time, timeout, retry, exit, stdout/stderr are recorded; public path-redacted derivatives are identified separately from private raw. Synthetic bundle data stays local, no new permanent Archive/Vault/Library claim is made.

Local test results do not prove normal Windows execution, CI execution, separate reviewer execution, original historical evidence custody, actual ACL/retention, real storage adapter, disk-full/ACL/file-lock faults, external approval authenticity, or universal controller termination. Each remains separate. No merge, Ready transition, main change, historical destruction, production permit, or other-repository HOLD release.
