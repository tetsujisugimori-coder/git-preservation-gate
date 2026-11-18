# PR #6 P2補訂・独立再審査

## 対象と限定結論
開始HEAD `5cb9a6e66de76f3de51f2ee52fe01d9aee347912`、tree `18f0f8856a495aa6e687f5c61bd42a5bf137fd52`。base/main `68285b5a12bf1ef2707543681ba3b3064c2339d4`。review [5954222207](https://github.com/tetsujisugimori-coder/git-preservation-gate/pull/6#pullrequestreview-5954222207)。開始時OPEN・Draft、指定HEAD一致。既存Issue #5 / branch / PR #6を維持。PR #4や元規約v0.1.0、初回原票は変更しない。

設計・合成範囲に限りP2-01/P2-02はCLOSED、Stage 0限定受入・限定マージ推奨YES。総合PARTIAL。正式採用PENDING、Stage 1開始NO、他repo適用NO、実permitはfalse。マージ・Draft解除なし。実原物/原ZIP/ACL/本番storage/保証された所有者承認の検査はNOT_TESTED。この報告は独立AIによる文書・合成審査である。

## P2-01
L3追加契約の空欄を安全PASSへ変換しない。risk_contractの対象risk、判断、理由、承認を固定する。基本検査で十分な承認済み理由がある場合はゼロ追加を許容し、不当なBLOCKEDを避ける。必須追加検査がある場合は従来の全必須検査を維持し、FAIL/UNKNOWN/NOT_TESTEDを別々に集約する。個別承認そのものの欠如と、追加安全契約の根拠不足は別の状態として記録。

## P2-02
分類が低すぎる場合の早期returnを、分類UNKNOWNと共通の既知FAIL保存へ統合。SHA FAILはverification FAIL、storage FAILはcustody FAIL、必須CI FAILはacceptance FAIL。未確認の別軸はUNKNOWN。全eligibleはfalse。独立追加審査で、分類不確実時にrisk_contract承認FAILが隠れる3境界も見つけ、同じ3件で修正確認した。

## 事前固定と失敗履歴
新32件は独立Bが修正実行前に期待を固定。oracle SHA `a48160852b060467659ee464c7f63b35b5f77328d6b3668b771b99a328828433`。旧checkerは5/32一致、27不一致。ただし新fieldを旧schemaが拒否するケースを含むため27件を既存欠陥数とは呼ばない。

旧49ケースの原入力・期待・過去実績は不変。補訂後に旧期待と比較すると47/49、差分はV019とV041。L3の追加契約未設定をUNKNOWNへ変えるという事前規則による変更であり、旧原票を上書きしない。別overlayで再判定する。初回overlayはV041の変更を見落とし48/49、その見落としを独立Bが訂正。初回overlay・失敗ログ・訂正記録を全て保持。v2 overlay SHA `04855410edbd754b5fdf4fe27e8acda21d6ae18a52f6002180571b7525257e07` は49/49。全期待が最初から完全だったとは主張しない。

独立追加X01〜03は実行前固定。修正前0/3、修正後3/3。追加oracle SHA `cb925c283ab1d670d14dcc2a3b60b222be899712ed48d25d2d169462da8b3e9e`。

## 最終検査
- 自己検査: 新32/32、補訂overlay49/49、追加3/3。
- 別AI担当B: 同じ新32/32、overlay49/49、追加3/3、旧schema29/29、旧runner故障4/4、PR4固定旧AT52/52。
- 修正checker SHA `e840f847edf8162114a2d4593d09ff0dce4fc0076bfa1b03a096f12f27eaea60`。
- 旧ATや初回49件の結果を改稿していない。SMの実運用を追加で試験したとは主張しない。
- 1操作timeout5秒、retry0の合成器原票に入力SHA・期待・実際・stdout/stderr/exit・時刻・環境を記録。旧ATは別runnerの有限期限を原票に記録する。

## 独立性・証拠
[独立再審査](p2-independent-review.md)は別AI実行枠、別取得作業域に固定ローカルcommitを取得して実行。共有基盤・同一アカウント・履歴継承・共有資産の限界があり、第三者人的/資格情報独立監査ではない。

初回manifestは初回HEAD限定として保持。今回の変更集合は `evidence/v0.2.0/p2/submission-manifest-final.json` に別固定。提出後の完全HEAD/tree、全提出pathのbyte/size/SHA/Git blob照合と正式CI実状態はPR追補で記録する。新Archive/Vault/Library保存は行わず、恒久保全PASSを主張しない。

## 残存条件
本件P2の閉鎖は実際の保存先/原物真正性を保証しない。旧案件のFAIL/BLOCKEDは維持。必要な最小次工程は所有者のStage 0正式採用判断と、採用後の案件別移行審査。実運用には別承認と実入力・権限・有限停止・証拠取得契約が必要。

## 新再実行runnerの追加是正
独立担当Bが新 `run_fixed.py` の空fixture/重複ID/必須field欠落で不正成功または原票欠落となる3反例を事前固定して再現した。新runnerへ非空・集合・shapeのpreflightを追加し、未実行はNOT_TESTED/exit2/rows0、実際の出力不正はFAIL原票保持とした。同じ3故障は3/3、正常32/32、不正stdout保持1/1を独立確認。旧runner故障4件の成功を新runnerの保証へ流用しない。初期P2原票・checker・oracleは変更していない。
