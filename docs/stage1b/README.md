# Stage 1-B: bounded trial execution and storage contracts

[Plan](PLAN.md) / [pilot boundaries](pilot.md). This is an additive implementation based on merged Stage1A and adopted central v0.2.0, not a change to historical observations. Issue11 tracks this stage.

## Distinct acceptance questions
1. Does a proposed contract structurally match a separately authenticated authorization and adopted policy?
2. Did the normal-user Windows process and bundle operation actually execute with bounded stop observations?
3. Did A create a saved object, receipt and manifest in the intended trial destination?
4. Did B independently retrieve that exact saved object and verify its bytes and restore?
5. Is that destination a valid durable store with the required ACL and retention?
6. Does the reviewed implementation qualify for its limited code/technical scope?

None automatically implies the others. No raw approval is published. JSON `authorization_verified=true` is an assertion from a trusted caller, not authentication performed by this prototype. P0 synthetic local trial authorization is not P2 durable storage authorization. Production permit stays false.

## Non-destructive behavior
Use only fresh task directories. Attempt reservations are create-only; interrupted attempts are not silently reused. Keep originals, receipts and failures. No cleanup, migration, overwrites, historical ZIP regeneration or privileged ACL changes. File/command failures are retained as actual FAIL/BLOCKED/UNKNOWN independently of whether their test verdict matches expectation.

## Evidence and independence
Original execution responses are retained separately from public redacted evidence. A transformed public log is not byte-identical to the raw source: its source SHA and derived SHA must be distinguished. A log generated from output is not a lost original's replacement. Windows and Linux results, PS5.1 and PS7, static review and actual execution, same-owner technical revalidation and third-party independence are reported separately.

Known boundaries: this prototype does not authenticate external approvals, guarantee a storage provider's retention, archive LFS/submodule internals, handle arbitrary hostile programs, issue production permissions or deploy to other projects. Those limits must remain visible in the final report rather than be concealed by synthetic PASS counts.
