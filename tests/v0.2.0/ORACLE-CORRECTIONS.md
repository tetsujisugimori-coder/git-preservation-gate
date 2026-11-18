# Independent oracle corrections

The initial 44-case oracle was fixed before seeing checker code. Initial implementation matched 24/44. The implementing agent identified two normative questions, not simply a demand to accept actual output. After independent examination:

- V013 original substitution: original-target custody and verification claims are invalid (FAIL), rather than PASS with only acceptance FAIL. Independence limitations remain separate. This rejects the initial implementation's unrelated independence FAIL.
- V008 and V040 invalid Level 1 classification: cannot emit ARCHIVE_NOT_REQUIRED. Applicability is conservative true; custody, verification, independence UNKNOWN, acceptance FAIL. Classification contradiction is not proof that stored bytes are corrupt. This rejects the initial implementation's blanket FAIL on all axes.
- V045 added independently: Level 1 must not require separate storage-scope/expiry/individual approval. Policy adoption and repository-specific CI/review remain required. This detects over-BLOCKED behavior.

Old oracle files and first-run observations remain unchanged. Corrected expectations were fixed before rerunning their new implementation. These changes strengthen original identity and truthful scope, not loosen a negative test to obtain PASS.

No human/credential independence is claimed for this reviewer AI. Shared infrastructure/account/workspace and inherited conversation remain limitations.
