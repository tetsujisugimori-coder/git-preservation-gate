# 中央保全・監査統合規約 v0.2.0 正式採用記録

## 承認・発効
- **所有者承認：YES**。承認日：**2026-11-18（JST）**。承認記録：[Issue #5](https://github.com/tetsujisugimori-coder/git-preservation-gate/issues/5)。
- **発効日：2026-11-18（JST）**。規範文書の切替は、この正式化PRが **mainへマージされた時点** から。マージ前の旧判定・旧承認を自動で変更しない。
- **現行正本**：[docs/v0.2.0/policy.md](policy.md)。詳細契約は [gates-and-audit](gates-and-audit.md)、[authorization-and-rescue](authorization-and-rescue.md)、[compatibility](compatibility.md)を参照。解釈が衝突した場合は新規運用を停止して規約改訂PRで調整する。
- **歴史的版**：[v0.1.0](../preservation-policy.md)は当時の規約本文を保存。PR #4のv0.1.1案は未採用、PR #6のStage 0提出時点の「未採用」は履歴であり、後続の所有者決定により正式採用へ切り替えた。

## v0.1.0からの変更点

|項目|v0.1.0|v0.2.0 正式採用|
|---|---|---|
|適用粒度|Git成果物保全を中心に横断要件|**成果物・原物・操作ごとにLevel 1/2/3分類**。混在PRも対象別に判断|
|通常コード・文書|保全ゲートの基本条項が一律必須と誤読され得た|**L1** はGit履歴・案件別CI/レビューを基本とし、追加Archive・ZIP・別担当・VM等は一律要求しない|
|重要原票・原ZIP|実保存・再取得・全byte・wrapper照合|**L2** として維持し、承認済み永続先のreceiptと実物再取得を必要とする|
|機密・重大破壊リスク|案件条件を別審査|**L3** はリスク別の追加安全条件の要否・根拠・承認を事前固定。別account/VMは一律必須でない|
|監査者分離|P05の異なるレビュー担当が基本、独立者不在でBLOCKED|**SOLO_STANDARD** の別session/別実行・別検証領域・直接再取得を条件として技術照合可能。ただし人的独立性はLIMITED_SHARED_OWNER、STRICT要件は別|
|判定|PASS/FAIL/PARTIAL/BLOCKED/UNKNOWN/NOT_TESTED|**CUSTODY / VERIFICATION / INDEPENDENCE / ACCEPTANCE** を別軸で保持。非適用はPASSにしない|
|承認|案件・保存先等を識別|対象・分類・保存先・主体・操作・権限・保持・削除条件・期限が一致すれば**既存範囲承認を再利用**可能|
|原物喪失リスク|受入完了まで保全ゲートを重視|**取得済み原物の先行保全救済**を許可済み範囲で可能にし、保存・再取得・受入を分離|
|既存結果|旧原票・FAILを保持|**追記型再審査**。来歴不完全と内容破損を分離し、証明できない履歴をPASSにしない|

Git bundleの自己完結性・空bare復元・全object照合が案件目的に含まれる場合はv0.1.0 P01/P02/P04の厳格な条件を維持する。既存の実証済みFAIL、必須CI、安全/機密停止条件を規約変更で消さない。

## 正式採用の対象範囲
1. **中央リポジトリ**：発効後に実施する規約の解釈と新規審査に適用。設計・合成受入と実原物の保全受入は別。
2. **Stage 1**：着手を承認済みで開発・試験中。PR #9のStage 1-A合成技術成果がマージされていても、Linux合成以外の本番動作、実保存契約、Windows、CI強制・process有限停止・実permitは未成立。 `production_permit=false` を維持する。
3. **他リポジトリ**：段階展開の計画・限定パイロットは承認済み。実際の採用は各repoのIssue/branch/PR、採用version/commit、成果物の分類、既存契約・証拠と追加承認の確認を経て判断。**一斉適用・既存BLOCKED/HOLD/FAILの自動解除は禁止**。
4. **個別の保存操作**：中央採用は保存・転送・削除・上書き等の実行承認を自動付与しない。既承認を流用できるのは、対象・機密区分・保存先・主体・操作・ACL・保持・削除・承認期間が具体的に一致する場合だけ。**PR #23の保存操作は中央採用だけで無条件承認されない**。未確認・範囲外は当該操作を停止して確認する。

## 証拠と境界
- [PR #6](https://github.com/tetsujisugimori-coder/git-preservation-gate/pull/6)は設計・合成範囲の限定受入、[PR #9](https://github.com/tetsujisugimori-coder/git-preservation-gate/pull/9)はStage 1-AのLinux合成範囲の限定技術受入。いずれも本番保存/取得/復元/権限/保持のPASSではない。
- 歴史的来歴不足に対する所有者の柔軟化承認は[Issue #5の記録](https://github.com/tetsujisugimori-coder/git-preservation-gate/issues/5#issuecomment-6976945433)に従う。[Stage 1-Aの来歴判定案](provenance-exception-proposal.md)は独立の拡張提案として保持し、全ての追加状態名・例外をこの正式化だけで本番必須契約に昇格しない。
- 過去の原物、旧原票、旧判定、旧規約commitは上書きしない。新判定は対象・採用版・新証拠・責任者・理由を追記。未取得原物を再生成物で偽装しない。公開GitHubには機密原物・内部locator・非公開承認票を記載しない。
