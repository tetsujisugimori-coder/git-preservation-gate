# Stage 1-A independent technical re-review (B)

Scope: synthetic bundle probe only. Production permit remains false. Reviewer B is a separate AI session and verification directory, with shared platform/account/filesystem and inherited history. This is not independent human or credential authority.

Baseline GitHub HEAD `7949e2fc642852b7b3c2463dc1ebc8a02afa565f` was independently fetched and executed. Its limited original roundtrip passed; original self-reports are not replaced by this test. New semantic oracle was fixed before inspecting the revised implementation.

Reviewed local fixed HEAD `575f91f8a6bb04a7c39299153f361b44e42a00f8`: 32/32 declared cases matched independently. Cases include real synthetic Git operations and clearly labeled state-contract injections. PASS in axes tests means contract evaluation success, not actual historical evidence integrity.

## Findings
P2-01 evidence-record false acceptance: incomplete command records, unfinished process state, nonzero command reported as success, contradictory verdict were accepted. Fixed and same five original inputs rejected. Thirteen stronger mutations derived from a complete valid normal record were also rejected, while original normal record accepted. Further mode-bypass (`normal` relabeled as state injection with empty commands) was discovered, fixed, and same input rejected; unknown scenario rejected. CLOSED for this synthetic contract scope.

Final recheck: 20 rejection observations = 5 original inputs + 13 complete-record mutations + mode bypass + unknown scenario. Not 20 real Git experiments. Earlier failing observations and original expectations retained.

## Limitations and decision
No remaining P1/P2/P3 found in reviewed implementation scope. Local synthetic technical acceptance YES, contingent on GitHub fixed-head submission readback and repeat execution before final recommendation. Durable storage/ACL/retention, real original evidence, Windows behavior, strong human independence, arbitrary descendant-process containment: NOT_TESTED or UNKNOWN as applicable. Timeout trial actually reaped the known direct child; this does not prove all possible descendant termination. Shallow/partial/alternates cases use synthetic markers/config rather than every real remote server variant. SHA-1 v2 bundle supported, not SHA-256 repository format or all Git bundle extensions. Historical provenance status remains separate from content and restoration. No merge performed.

Public evidence files are redacted derivatives with absolute workspace prefixes replaced; raw originals retained. Source hashes are not hashes of transformed files. GitHub fixed-head verification is pending and must be appended, not assumed.
