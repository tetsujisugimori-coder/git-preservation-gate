# Fault evidence categories

Test verdict PASS means the frozen expected handling occurred, not that the faulted save succeeded. Case status and test verdict are separate fields in every suite result.

|Requested condition|Current evidence category|Limit|
|write/read denial|Synthetic injected EACCES|Real ACL denied save NOT_TESTED; no ACL altered|
|missing destination / wrong scope|Real absent synthetic directory / scope input|Bounded local paths only|
|capacity exhaustion|Injected ENOSPC|No real disk exhaustion performed|
|file lock|Injected sharing violation plus separate normal-Windows exclusive read-lock measurement|Only observed regular-file sharing mode, not every device/lock|
|same name / simultaneous attempts|Real create-only duplicate and two receiver processes|Non-adversarial local owner; no universal race-proof claim|
|source mutation / partial write|Instrumented synthetic fault|Not old raw evidence; preserve incomplete attempt|
|process exit during save|Independent B bounded receiver termination test|Observe receipt absence/rejection, not universal crash consistency|
|receipt missing/corrupt, manifest/hash mismatch, missing saved file|Fault-copy mutations|Original successful objects unchanged|
|reconnect/readback unavailable / receiver cannot start|Absent path / nonexistent receiver process|Not all network loss modes|
|actor mismatch|Contract input and observed normal Windows subjects|No authentication built into JSON scope checker|
|traversal / links / junction|Path schema and real normal-Windows junction rejection|Symlink creation unavailable in normal Windows suite remains NOT_TESTED|
|Unicode / long path|Ordinary Unicode real-file success; long-path fixture creation failed before adapter|Long-path adapter acceptance NOT_TESTED, no setting change|
|L1 non-applicable / L2 missing / L3|Explicit non-applicable NOT_TESTED; mandatory rejection/unsupported|Issue14 defaults not duplicated; adopted risk classification unchanged|
|timeout / controller failure|Cooperative deadlines, bounded receiver and existing owned-Job observations|Kernel I/O hangs/controller death/universal descendants UNKNOWN|

Initial hosted-Windows formal suite failed and remains an independent CI fact. Normal Windows successes cannot overwrite it. New diagnosis and any platform-specific test-applicability change are additive records, not edits to the original oracle.
