# 実例から学ぶ保存・受入・マージの分離（Codex-Orchestration-Lab PR #23）
記録日：2026-11-19 JST。種別：**中央v0.2.0の適用例・運用補助資料（非規範）**。

現行の正式規約は [policy v0.2.0](../v0.2.0/policy.md)、[Gate A/B/C](../v0.2.0/gates-and-audit.md)、[承認再利用・原物救済](../v0.2.0/authorization-and-rescue.md)。本書は新たな義務・本番permit・他repoのマージ許可を作らない。各案件の`SECURITY.md`・既存契約・現行HOLDを優先する。

## 1. 事例の対象と確認根拠

- [Codex-Orchestration-Lab PR #23](https://github.com/tetsujisugimori-coder/Codex-Orchestration-Lab/pull/23) / [Issue #22](https://github.com/tetsujisugimori-coder/Codex-Orchestration-Lab/issues/22)。マージ対象HEAD `c4dde4c01343dab3bb57dfd13c254af35a8628c6`、差分は`AGENTS.md`42行と`.gitignore`1行。**Level 1の通常Git管理文書**。
- 別件で救済した固定7原物（6文書＋元manifest、計45,645 bytes）は**Level 2の重要原物**。通常Windowsユーザーが2026-11-19 10:46 JSTに承認済みArchiveの新規領域へcreate-onlyで保存。同日10:58 JST、別PowerShellウィンドウから別Python監査手順で保存先を直接再取得し、7/7件の全byte・size・SHA・manifest照合をPASSとした（提出Windowsログに基づく）。同じ所有者/Windowsアカウント/hostを共有し、`INDEPENDENCE_STATUS=LIMITED_SHARED_OWNER`。第三者人的独立性PASSではない。[所有者による対象限定受入記録](https://github.com/tetsujisugimori-coder/Codex-Orchestration-Lab/pull/23#pullrequestreview-5969512259)。
- Level 1文書2ファイルは、固定差分・正式CI（2 workflow、Windows/Ubuntu計4 job）・限定技術レビュー・所有者判断で[文書限定の正式受入PASS](https://github.com/tetsujisugimori-coder/Codex-Orchestration-Lab/pull/23#pullrequestreview-5969625709)。追加Archiveは非適用（`NOT_TESTED`）で、Level 2の保存契約を流用しない。
- [マージ直前のレビュー](https://github.com/tetsujisugimori-coder/Codex-Orchestration-Lab/pull/23#pullrequestreview-5969815850)は2026-11-19 14:33:32 JST時点で`MERGE=HOLD/NO`。GitHubでは同日14:36:49 JSTに[merge commit `9190483e6148…`](https://github.com/tetsujisugimori-coder/Codex-Orchestration-Lab/commit/9190483e6148c654ac0d31cf5a0262c344956bf0)が成立。今回参照できたGitHub記録から、最終HOLD後の操作主体・追加承認・規則適合の全経路は特定できない。詳細は[マージ後追補](https://github.com/tetsujisugimori-coder/Codex-Orchestration-Lab/pull/23#issuecomment-7002297135)。**マージ実績は観測事実、マージ許可の証明ではない**。
- 旧ZIP同一性UNKNOWN、H11 MISMATCH、歴史的P2-01〜04 OPEN、C01〜C30 NOT_TESTED、実Codex B起動禁止などは本事例の成功で解除していない。

## 2. 他案件でも使う最小運用手順

1. **受入単位と依存を固定する**：対象repo、Issue/PR、HEAD/tree/base、成果物ID、採用規約版、案件契約、現在の判定を明示。通常Git文書、重要原物、特別リスクを対象ごとに分類し、混在PRでは独立した判定票・依存関係を作る。過去の欠損・別案件のP2は、現在の受入必須条件に**関係する場合だけ**停止理由にする。既知の安全FAILは無関係として握りつぶさない。
2. **Level 1は通常Git管理を既定とする**：固定版・必須CI・レビュー・権限を確認。明示指定がない限り、追加Archive宛先・保持・ACL・A/B分離の入力を求めない。追加保存を個別に指定したときだけ、その操作に必要な追加情報・承認を確認し、別判定する（[Issue #14](https://github.com/tetsujisugimori-coder/git-preservation-gate/issues/14)）。
3. **Level 2は許可範囲内で先に原物を保護する**：既存承認を対象/保存先/主体/操作/権限/保持/削除条件/期限で照合し、一致項目は再利用。不足箇所だけを確定。原物に触れず読取検査を行い、承認済みの新規領域に非上書き保存し、manifest/receiptを記録する。サンドボックス書込拒否と通常Windowsユーザーの権限を混同しない。承認不足・機密疑義・ACL拒否では保存を停止する。
4. **Bは実保存先から再取得する**：Aのstdout、実行ID、監査プログラムのPID差だけで別セッションを認定しない。別セッション/別executionと使用検証器・共有資格情報を記録し、保存先の実bytesと元基準でsize・SHA・全byte・適用時CRC/ZIP manifest・Git bundle復元を照合。共有owner/hostは`LIMITED_SHARED_OWNER`。再保存や必要以上の再監査は繰り返さない。
5. **4軸を分けて判断する**：`CUSTODY`（保存）、`VERIFICATION`（保存先照合）、`INDEPENDENCE`（独立性）、`ACCEPTANCE`（対象受入）。未実施は`NOT_TESTED`、取得不能は`UNKNOWN`、拒否は`BLOCKED`、不一致は`FAIL`。Level 1追加Archiveの非適用はPASSに捏造しない。必要条件を満たした成果物だけ所有者が明示受入する。
6. **マージ/pullは別の実行ゲート**：受入PASSやGitHub APIの操作可能性だけで許可済みとしない。案件の現行禁止、許可主体、レビュー、保護/required checks、直前HEAD等を確認。不明・禁止中は実行停止。GitHubでマージが後から観測された場合、コミット/時刻/観測状態と当時のHOLDを併記し、承認・実行主体が未確認ならUNKNOWNとして**遡及的なAPPROVEを作らない**。ローカルpullは独立に承認する。

## 3. 今後の共通化と非対象

- 共通化するのは「レベル/受入単位の早期分離」「既存承認の再利用」「create-only保存と直接再取得」「4軸と独立性の限界」「受入とマージ許可の別記録」。新しいL3要件・本番保存機能・一律自動マージの導入ではない。
- Windows操作の自動化は[Issue #15](https://github.com/tetsujisugimori-coder/git-preservation-gate/issues/15)／[Issue #18](https://github.com/tetsujisugimori-coder/git-preservation-gate/issues/18)の別工程で扱う。既存のLevel 1入力簡素化は[Issue #14](https://github.com/tetsujisugimori-coder/git-preservation-gate/issues/14)。本書はWindowsシステム設定、ACL、GitHub権限、作業中PRの状態を変更しない。
- 後続案件へ適用するときは、対象固有の契約、分類、権限、停止条件を毎回確認する。本例で成立したLevel 2の技術受入を別repoの原物や本番permitへ自動流用しない。

## 4. 最小限の引継ぎ記録テンプレート

```text
対象：repo / Issue / PR / HEAD / tree / base / 成果物ID
分類：Level / 判定理由 / 必須依存 / 対象外の旧阻害
承認：既存承認の適用範囲 / 不足条件 / 操作主体 / 期限
保存：対象・保存先の参照ID / attempt / custody / manifest・receipt
再取得：Bのsession/execution / 保存先直接取得 / 検査値 / 共有要素
判定：CUSTODY / VERIFICATION / INDEPENDENCE / ACCEPTANCE
PR操作：CI / レビュー / 現行禁止・保護 / 別マージ許可 / pull許可
履歴：旧判定（不変） / 新観測 / UNKNOWN / 人間の明示判断
```
