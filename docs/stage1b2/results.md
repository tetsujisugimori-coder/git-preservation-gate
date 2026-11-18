# Stage 1-B2 observations and acceptance boundary

Start main `732175213158b11b0f91529ee0d10c17ad6ea4fe`; merged PR12/tree13530cf0. Existing policy, Stage1A/1B code and fixed oracles remain unchanged. Issue15 / Draft PR16. Level1 input normalization remains Issue14.

## Actual Windows pilot
Owner approved this newly generated nonsecret synthetic pilot, new Archive subarea, automatic create/read and separate-session retrieval, retention one year. Private locator/approval source are not public. Direct and one-shot receiver each saved three new plain/Unicode/binary objects with final manifest/receipt under ordinary non-admin Windows permissions. No existing evidence was altered or ACL changed.

Independent B newly read each saved Archive directory directly in a separate Windows execution/area and used an independent pathlib/hashlib audit. Direct:5 files/1686 bytes; handoff:5 files/1691 bytes. Each contains3 original objects plus manifest/receipt. Source/store/retrieved full bytes, sizes, SHA, exact file set, manifest/receipt hashes and IDs matched. This is actual synthetic-file Archive save/readback, not just a workspace copy or A's report. Receipt retention date is recorded; enforcement and long-term availability remain UNKNOWN. No ZIP used, CRC NOT_APPLICABLE. No real-project evidence moved.

The one-shot receiver really launched and read the authorized source itself. Both observations use Windows-local reachable source and Archive. Arbitrary cloud-to-Windows transfer is NOT_TESTED; it is not proven by renaming a manual copy. Direct normal-user execution was available, so no sandbox settings or daemon were installed.

## Test scope and preserved failures
Linux fixed34 and boundary5 passed. Independent B's additional cases include actual bounded interrupted receiver and receipt-absence rejection. B found malformed risk list caused an uncaught AttributeError before save. This P3 was corrected by risk schema validation, with frozen4 RED0/4 → GREEN4/4 and unchanged34+5 regression. B's original BLOCKED expectation and justified FAIL/SCHEMA overlay are separately preserved, not silently rewritten.

Normal Windows PowerShell5.1 and7 on first published candidate each:33 PASS,0 FAIL,1 NOT_TESTED of34 (symlink creation permission unavailable), plus boundary5/5 and old finite21/21. Actual exclusive read lock yielded BLOCKED/no receipt; source and destination junctions were rejected; long-path fixture creation failed before adapter invocation, therefore long-path handling NOT_TESTED. Follow-up fixed-version repetitions and exact source identities are in the public audit records.

Injected ENOSPC/EACCES/sharing faults are not actual disk-full/ACL-failure tests. Controller death, hostile ancestor replacement, kernel I/O hang and universal descendant termination remain outside demonstrated guarantees. No privilege relaxation to improve scores.

## Formal CI history
Initial run44411775221 and diagnostic run44412388434: Linux success, hosted Windows failure. Diagnosis directly observed Windows admin token=true and ELEVATED_WINDOWS_TOKEN rejection. Generic BLOCKED matches in that failed run did not exercise intended per-fault behavior and are not claimed fault coverage. Old failures are retained.

Hosted admin rejection is now a separate frozen test applicability condition: verify adapter refuses before save and marks normal-user save suite NOT_TESTED. Normal-user Windows results are separately required and actually measured. Hosted finite-job regression is separate. Final-head CI result is checked and reported in the final anchored review rather than inferred from earlier runs.

## Four axes
CUSTODY: PASS only for the two specifically approved synthetic Archive objects and corresponding receipts, not all raw history or all repositories. VERIFICATION: PASS for the directly retrieved bytes and listed checks. INDEPENDENCE: LIMITED_SHARED_OWNER (distinct AI context/operation/area/method, shared owner/host/platform). ACCEPTANCE: limited technical judgment awaits final fixed-publication independent review; production remains unaccepted.

Production permit false; Stage1-C/HOLD and other repositories' old HOLD/BLOCKED unchanged. No merge or Ready. Historical path-publication P3 and old cloud raw-retention UNKNOWN are inherited, not erased by this pilot.
