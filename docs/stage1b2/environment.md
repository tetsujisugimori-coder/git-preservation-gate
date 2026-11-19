# Windows environment diagnosis (read-only)

Observed by a separate Windows execution session, normal owner account. No settings or ACL changed.

|Cause|Observation|Conclusion|
|---|---|---|
|A1 sandbox|Default CLI reports read-only, no writable roots; Low integrity token. Official reviewed command route yields same owner, non-administrator, Medium integrity.|Sandbox restriction confirmed. Official per-command authorization is not administrator elevation; its availability is not general write permission.|
|A2 Windows ACL|Archive listing/ACL readable. Owner FullControl; sandbox group ReadAndExecute.|Read access observed; subsequent non-writing OPEN_EXISTING directory handle checks for LIST/ADD_FILE/ADD_SUBDIRECTORY succeeded under the non-admin Medium token. Actual save remains separate; no file was created by this rights probe.|
|A3 subject|Same owner; integrity differs by supported execution route; administrator role false.|Identity/integrity observed, no claim of independent credentials.|
|A4 transfer|Windows GitHub source acquisition previously worked; actual new one-shot receiver path awaits pilot.|Source reachability must be measured, not inferred from design.|
|A5 workspace|Current workspace available. Previous unrelated cloud raw retention remains UNKNOWN.|Temporary workspace is not durable store.|
|A6 other|No general deny bypass attempted.|Other effective-access conditions UNKNOWN.|

Scoped search of gate-related work areas for approval/authorization/storage-contract/consent records found policy references, not a specific Stage1-B2 Archive authorization. Archive index had no gate-specific item; no gate Archive child was observed. This is non-discovery within the searched scope, not proof no approval exists anywhere. Concrete pilot authorization is requested separately.

Raw identity/ACL output is retained privately on Windows; public documentation intentionally omits internal locations and account details. Neither directory creation nor writing was used to diagnose initial access. New synthetic test output uses an authorized fresh work area; Archive pilot is separately gated.

## Subsequent owner approval
After the read-only investigation, the owner explicitly approved newly generated nonsecret synthetic objects, manifests, receipts and test records in a dedicated new area under the existing Windows Archive; automatic save and separate-session direct retrieval; retention one year from save; no existing-item deletion/move/overwrite or ACL change. This approval is specific to the pilot, not all repositories or production gates. Private source approval and exact destination are not published. Effective retention enforcement remains UNKNOWN.
