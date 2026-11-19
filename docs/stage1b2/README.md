# Stage 1-B2 — scoped Windows save pilot

Issue15 / Draft PR16, base `732175213158b11b0f91529ee0d10c17ad6ea4fe` after merged PR12. Adopted policy and old implementation/oracles unchanged. Issue14 remains the separate Level1 input-default change.

[Plan](PLAN.md) · [environment](environment.md) · [design](design.md) · [implementation and retained failures](implementation.md) · [results](results.md) · [fault coverage](fault-coverage.md) · [CI history](ci-history.json).

Observed: ordinary non-admin Windows automatically saved two approved nonsecret synthetic objects (direct/one-shot receiver) and a separate Windows raw-evidence bundle. Separate B session directly re-acquired the Archive objects, checked full bytes/size/SHA/manifest/receipt and ZIP CRC/internal manifest where applicable. Shared-owner technical verification is not third-party human independence. Actual ACL/retention enforcement is not inferred from a matching receipt.

Overall **PARTIAL; limited technical acceptance YES and limited merge recommendation YES**, with final documentation-only HEAD readback and exact-head CI recorded in the anchored PR16 review. Independent B rechecked the corrected code and same counterexamples; new schema P3 and CI aggregation P2 are CLOSED. No production permit, Stage1-C transition, other-repository deployment, Ready or merge. Long-path coverage, arbitrary cloud transfer, real disk-full/ACL-denied behavior and controller-wide hard termination remain incomplete; injected faults are labeled. Hosted Windows CI checks elevated-token rejection, not ordinary-user save success. Normal Windows measurements are separate.

New public evidence resides under `evidence/stage1b2/`; old regression derivatives under `evidence/stage1b2-regression/`. Private original locators and approval transcription are omitted from public summaries; originals remain in their approved location. Later probe/readback reports are explicitly outside the earlier frozen Windows raw ZIP.
