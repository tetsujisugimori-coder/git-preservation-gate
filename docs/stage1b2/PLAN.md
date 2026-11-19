# Stage 1-B2: scoped save / one-shot receiver pilot

## Preregistered boundary (2026-11-18 UTC)
Start main/merged PR12 commit `732175213158b11b0f91529ee0d10c17ad6ea4fe`, tree `13530cf019dbed8b8a80cc6a5aff4f4420233358`. PR12 head `7abbdca212f3c186948b04a7b42cb1d84fd86b2e`; its limited acceptance does not authorize production storage. No AGENTS.md in starting tree. Related issues5/11/14, new tracking15. v0.2.0 policy/gates are adopted and unchanged.

New nonsecret synthetic objects only. No existing case originals, no external data transport without matching authorization, no setting/ACL changes, no elevated Windows user, no permanent service/task registration. Production permit always false. A finite one-shot receiver is a prototype, not sandbox escape or an authenticated service.

## Frozen phases
1. Read Windows identities, sandbox/writable roots and ACL. Read-only successful access is not proof of write access. Distinguish A1 sandbox/A2 ACL/A3 identity/A4 transfer/A5 workspace lifecycle/A6 unknown.
2. Freeze synthetic cases and expected outcomes before executing new adapter. Implement create-only scope-bound save, staging and final receipt, direct readback and one-shot receiver. Keep old code/fixtures unchanged.
3. Run Linux tests, normal Windows PS5.1/7, independent B cases, existing regression32/50/10/18/21 and review boundaries. Real fault vs injected fault reported separately. No fill-disk or ACL manipulation to force real failures.
4. Actual Archive pilot only after concrete objects/root/actor/operations/retention/permissions approval matches. Missing approval blocks this operation, not safe implementation. Synthetic workspace success never means durable custody.
5. Independent B directly retrieves saved objects in a separate execution/area; exact original bytes, size/hash, manifest, receipt, IDs checked. Shared owner remains LIMITED_SHARED_OWNER.
6. Dedicated Draft PR; exact published HEAD readback, CI and independent technical review. No merge/Ready/production/other-repository rollout.

## Expected safety outcomes
Normal authorized synthetic save succeeds and verify requires original bytes. Existing attempt/file collision rejects with no overwrite. Unknown approval/scope, links/reparse points, traversal, changed source, invalid receipt/manifest/hash/identity, incomplete destination reject or explicitly remain UNKNOWN/BLOCKED. I/O faults cannot become successful custody. Process timeout/cleanup uncertainty is not success. Existence/ACL display alone is not observed effective write permission.

Level1 ordinary Git archive non-applicable remains NOT_TESTED and independent of basic Git acceptance. Issue14 owns default-input normalization; no duplicate edit to old contract. This storage adapter requires explicit archive intent and cannot silently reclassify L2/L3. Confidential/L3 input is unsupported pending individual security contract.

## Time and preservation
Each automated test runner has a finite outer timeout and retries0. Preserve first failed attempt and use new output areas for subsequent runs. Public logs are separate path-redacted derivatives; originals stay where generated. Publication scanner is a known-pattern check, not an all-secrets guarantee. Permanent ACL/retention guarantee is separate from local bytes and receipt integrity. Archive approval, raw custody and final acceptance are separate states.

## CI preflight
New dedicated workflow only triggers pushes to this pilot branch, contents read-only, checkout plus Python synthetic cases/regressions,10-minute job bounds. No credentials, deployment, services, settings, artifacts upload or real Archive targets. Existing workflow is unchanged and scoped to the old branch. CI temporary files are synthetic, not actual owner Archive storage. Native Windows normal-user measurements are separately required; hosted success is not their substitute.
