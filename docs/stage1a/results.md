# Stage 1-A 継続検証結果 (2026-11-18)

## 判定範囲
合成Linux Git bundleプローブの限定技術受入を審査する。実原物の永続保全、Windows、全process子孫の停止、資格情報分離、第三者人的独立監査は受入対象外。`production_permit=false`を維持する。

開始PR #9 HEAD `7949e2fc642852b7b3c2463dc1ebc8a02afa565f`、tree `b0d556e1cc5b3f6124ebdbed15394adf9679383e`、main/base `b8940d5d9824d50c9fc206b7584d5e84bfc8b671`。既存Issue #5/#7/#8、branch `feat/stage1a-synthetic-bundle-probe`を継続。Issue #5の所有者承認はStage 1開始・段階展開の根拠であり、未採用提案の自動正式化ではない。

## 保存した履歴と変更
旧提出probeを固定HEADから取得して再実行しPASS。過去の2回成功の報告は保持し、今回の結果と混同しない。独立担当も旧版を別取得・実行した。旧版は起動不能で記録を残さず例外終了することを別反例で確認した。

今回、合成3 commit/2 branch/tag、固定manifest、v2 SHA1 bundle検査、別storage/readback、空bare復元、全ref/object内容・commit tree/parent照合、fsck、期限付き実行原票を追加した。正常bundleを保持し、故障注入は複製だけで実行。既存証拠、他repo、Git設定、CI workflowは変更しない。

## 試験
固定oracle `cases.json` SHA-256 `ccebf7b7a83d148d730b2f7c7ad4f22b63255f747af8b1d9d2bed68514533ae4`。実装担当最終runは32/32期待一致。正常復元2件、実Git/ファイル故障、プロセス失敗、状態契約注入を`mode`別に記録し、合計を製品実測件数とは呼ばない。各入力・期待値・実値・コマンド・stdout/stderr・exit・時刻・checker/runner/oracle SHAは[evidence](../../evidence/stage1a/implementation/suite.json)を参照。

故障のactual=FAIL/BLOCKED/UNKNOWNに対するverdict=PASSは期待した拒否であって保全成功ではない。prerequisite/浅い履歴/promisor/alternatesを拒否。manifest欠損・差替え・破損、bundle破損、復元先汚染、保存/取得不能、Git起動不能・非ゼロ・timeout、例外、終了UNKNOWN、原票欠損を区別した。状態契約注入は実際に停止不能processを生成した試験ではない。

各コマンド上限8秒、timeout反例0.2秒、停止後直接子wait2秒、再試行0。POSIX process groupを停止し直接子reapを確認した。全子孫・悪意あるdetachや非POSIXの停止保証はUNKNOWN/NOT_TESTED。実物のLibrary/Archive保存は今回追加せず、試験用領域の往復だけをPASSとする。

## 独立レビュー
別AI担当Bが別clone/実行領域で原入力・oracleを保持して再検証。担当AとBは同一基盤・アカウント・共有workspaceであり第三者人的独立ではない。

P2: 不完全な成功原票とscenario/mode偽装が受理される問題を発見。成功票の必須フィールド、型、process/exit、期待値とverdict、既知scenario/mode対応を補訂。元のB01〜B05と型13変異を再検証。最終固定GitHub版の再取得結果はPRレビューに追記し、提出前検査と区別する。

## CI・保全・次工程
開始時GitHub Actions/checksは0件、正式CI NOT_TESTED。合成自己試験をCI PASSにしない。新workflowは不要として追加しない。公表ログは内部パスを置換した派生票でraw SHAを保存する。原ログ・合成bundleは案件領域に保持し、永続保存保証には昇格させない。

内容/来歴/復元/独立性の四軸を分離する補助関数と合成3例を追加。過去原物の真偽・承認を認証する機能ではない。来歴例外は提案として残す。

castle-3d-partsは[読取調査](castle-pilot-survey.md)のみ。通常check成功と未解決専用FAIL/BLOCKED/HOLDを別扱い。18 workflowのPR起動とnative/browser副作用があるため、導入は別の限定パイロット審査へ引継ぐ。横断開始の一律再承認は要求しないが、無審査の本番変更はしない。

Stage 1-B: Windows/実保存先/厳格分離/本番用途は未実装・別受入。Stage 1-Aの技術受入とPR限定マージ推奨は固定版独立レビュー後にPR本文で確定する。マージはしない。
