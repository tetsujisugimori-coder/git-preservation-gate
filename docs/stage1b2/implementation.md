# Stage 1-B2 adapter implementation / self-check

Scope is a **nonsecret synthetic file pilot**, never production permission. Adopted v0.2.0 is unchanged. Old Stage1A/1B code, fixtures and oracles are unchanged. Level1 input normalization remains Issue14; this adapter recognizes explicit archive-non-applicability but does not fill old contract fields or authenticate owner approval.

## One-shot API
`python tools/stage1b2/adapter.py save --request <request.json> --approval <separately-verified-approval.json>`

`python tools/stage1b2/adapter.py retrieve --saved <destination/attempt> --original <original-source> --receipt-sha256 <fixed-receipt-digest>`

Request binds synthetic-only status, nonsecret risk flags, level, object kind, operation mode, actor, object ID, unique attempt, source/destination absolute roots, and nonempty path/size/SHA item set. The separate trusted approval binds the exact canonical request SHA, source/destination, actor/object/mode, validity, retention, ACL confirmation and create/read operations. The record's `authorization_verified` value is **not authentication**; the integrating controller must verify actual owner authorization independently. A user-controlled request plus a fabricated approval cannot be treated as an authorized controller call.

Save reserves a fresh attempt directory, captures bounded source bytes, creates staged files exclusively, fsyncs and reads them back, verifies source bytes again, and renames staging only within the new reserved attempt. Manifest and receipt are created exclusively. Receipt is written last; interruption never earns success. Failed attempt directories and failure records remain, retry with the same attempt is refused without modifying existing successful evidence. Independent retrieval enumerates the destination directly, validates receipt digest, manifest and exact file set, and compares original bytes.

Paths reject escaping, drive/UNC item names, casefold duplicates, Windows reserved names, symlink/reparse ancestors and unexpected directories. Trusted roots must be absolute without parent traversal. No ACL changes, elevation, task registration, service or deletion is performed by the adapter. Windows admin tokens are rejected. Linux root in a synthetic container does not count as a normal-Windows execution.

Handoff is a **one-shot receiver process**, not a daemon. The fixed test invokes the CLI in a separate process, which itself reads the reachable approved source and saves it. It does not establish cross-host transfer; a source inaccessible to the receiver remains blocked. Direct path is preferred. No sandbox relaxation or security bypass is implemented.

## Limits
Only bounded ordinary files (max64, aggregate16MiB) are supported. Level3 or non-synthetic originals are blocked, not silently downgraded. ZIP/bundle structural acceptance is not provided by this file adapter; their required wrapper checks remain separate. Retention is a recorded contract, not proof that the filesystem enforces it.

Cooperative timeout cannot bound a kernel/OS filesystem hang. The controller must use the existing finite-process mechanism for Windows observations; controller death and universal descendant termination remain separate UNKNOWNs. Directory rename/completion is not a universal crash-atomic or power-loss durability guarantee. There is no guarantee against a malicious actor concurrently replacing trusted root ancestors; such strong-authenticity cases are unsupported. ACL inspection must happen outside the adapter; no synthetic approval field proves effective ACL.

## Frozen tests and retained failures
`tests/stage1b2/oracle.json` froze34 cases before first execution. First runner incorrectly parsed only the last digit of case IDs:13 matches/21 failures. Initial runner/source/result records are retained. Correcting case selection without changing inputs or expectations produced34/34.

Five further expectations were independently frozen in `boundaries.json`: relative-root rejection, malformed manifest item, boolean size, extra empty directory and malformed receipt. Hardening initially exposed a runner path-normalization bug: `Path.absolute()` retained `..` in the fresh test root, so18 cases were properly rejected; the boundary runner stopped at its prerequisite assertion. Old runner/source/result records are preserved. The test harness alone now canonicalizes its own newly created root. Final34/34 and5/5 match, exits0; no expectation was fitted to outputs.

Fault outcomes and test outcomes are distinct. ENOSPC, ACL denial and sharing violation cases are explicitly **injected**, not actual volume-full/ACL/file-lock measurements. Link creation may be unavailable on normal Windows and then is NOT_TESTED. The harness records that result without claiming the real fault passed. Fault-copy mutations affect fresh synthetic copies, never archived original evidence.

Commands: `python tests/stage1b2/run_suite.py --root <fresh-root>` and `python tests/stage1b2/run_boundaries.py --root <different-fresh-root>`. The suite does not claim independent-person review; another session must obtain the published fixed version and audit saved objects separately.
