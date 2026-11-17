# Stage 0受入と引継ぎ

## 調査（2026-11-17 UTC、提出前）
- 正式名/所有者: tetsujisugimori-coder/git-preservation-gate、Public、default main。
- 開始HEAD `0cd175a56ca4c8689d02fabdf2f2e05b8acaf344`、tree `6d189b24b7c1de174d7afe0b70e70d889e3e866b`、root commit 1件。
- tracked fileはREADME.md 1件のみ。AGENTS.md/ローカルskills/workflowなし。既存README題名を保持して拡充する。
- 開始時branch mainのみ、Issue0/PR0（全状態一覧）。Issue1と専用branch docs/stage0-preservation-contractsを新規作成。
- GitHub metadataは現在接続のpermissions admin/maintain/push=true、所有者permission APIもadmin。ただしAPIのadministration許可とは別。
- rulesets一覧0件、branches main protected=false。branch-protection詳細APIは403、詳細UNKNOWN。強制保護ありとは認定しない。
- workflow一覧APIはconnector非対応。tree内workflow0、Actions runs0。Actions設定詳細UNKNOWN。設定変更なし。
- 既存README以外の規約なし。main直変更禁止・承認済み保存・案件分離という依頼方針との衝突なし。共通規約の実採用は別工程。

## Stage0の受入条件
指定8文書、相互リンク、規約正本、全要件の追跡、状態/許可分離、全故障仕様、Public安全性、固定差分を自己点検する。設計の独立文書レビューと実物の最終確認を行うが、所有者による正式受入は別途。Stage1試験を実行せず全NOT_TESTEDとする。

## 判定分離
- Stage0設計の成立: 本PRの文書審査対象。
- Stage1開始準備: 仕様は入力になるが承認・実行基盤が未確定でNOT_READY。
- ゲート技術成立/本番保全: NOT_TESTED。
- 実repo適用: NO、Stage3で別承認・審査。
- merge: 独立文書レビューと最終提出実物の再審査後に限定推奨を報告する。実mergeしない。

## Stage1開始の最小条件（OPEN）
1. ownerが合成repoだけの実装・故障試験範囲を承認。
2. Git/object format・OS対応表、隔離機構・全process期限/終了方式、容量上限、retry/cleanup契約を固定。
3. 合成データ用の保存先と保持期限/ACL確認方法・独立取得担当を承認。
4. schema/理由コード・機械判定仕様とテストfixtureを独立審査。秘密や実案件を使用しない。
5. 規約/検査器自身の保全・復旧責任者、証拠署名/不変性の必要強度を決定。

未決の値を推測で埋めない。準備できた文書と未実装ゲートを混同しない。実装開始指示が来るまでStage1を開始しない。

## 要求対応
|要求|正本/具体化|
|---|---|
|保全対象・完了条件|規約P01〜P08|
|保存承認・機密・停止|security-and-storage、規約P03/P06/P09|
|Gate A/B/C・強制力|gate-contracts|
|AI採用・版・更新責任|ai-integration-plan|
|信頼境界/来歴|architecture|
|正常/故障試験|tests/test-plan.md|
|提出/受入/後続の境界|本文書|

検証結果、最終HEAD/tree、独立レビュー対象hash、提出読戻し、CI状態はPRの最終報告に記録する。自己参照hashを文書内へ再帰的に埋めない。CIが0件なら未実施とする。今回CI新設はしない。
