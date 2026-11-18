# castle-3d-parts 初期パイロット候補・読取専用調査
観測日時: 2026-11-18T11:46:09Z。担当: castle_pilot（別AI担当枠、同一基盤・共有workspace）。外部変更・push・CI再実行・原証拠の変更なし。

## 固定対象
- PR #41: OPEN / Draft / 未マージ。HEAD `7b2dceee7e42075bbd03967a139fd48f1fd55624`、tree `af5e59fe03bfa62dd8b6433b7acf46fca6f01bf5`。
- branch `feat/stage3d5d-direct-occt-proof`、base `feat/stage3d5c-native-proof` / `923bda856015398e1578f66bfc9b5d6553cf49a1`。未マージPR #40上のstacked PR。
- main `18ffb29eeb3db067d47513f76e3a2ef44865c45a`、tree `423d33c5a8283445832ea3c5495dc94090796090`。
- main AGENTS.mdを読取。GitHub正本、Issue→branch→Draft→独立レビュー、固定版監査と無関係変更の分離、CI成功≠マージを要求。別アカウント・VMの全件必須は見当たらない。

## CIと起動リスク: 現在のAPI観測
固定PR HEADのActions一覧は18 run、全件completed/success。check-runsは29件、全件completed/success。これは既存実行の状態確認であり新規実行・原artifact再監査ではない。
PR HEADのworkflow19本を実取得し、on節を確認した。pages.ymlを除く18本がpull_requestを受信し、path制限はない。checks.ymlはpush/mainも受信。pages.ymlはpush/mainおよびworkflow_dispatchでPages deployする。その他の一部にはworkflow_dispatchもある。
stage3a/b等にはChromium/WebKit、stage3d系にはFreeCAD native処理がある。従って文書だけの新規PRでも既存CIの実行が起こり得る。「Level 1だから無副作用」とはしない。
当該19本にissue_comment/workflow_runイベントは見当たらないが、外部Apps/Webhooksの不存在を意味しない。外部設定は今回未監査・UNKNOWN。main branch応答のprotected=falseは、全rulesets・外部統制の不存在証明ではない。

## 旧判定と証拠: 既存報告として継承する範囲
PR本文と最終報告はStage3-D-5D PARTIAL/HOLD、限定マージNO。18/29の既存CI成功とは別に、専用5D CIは追加path契約によりBLOCKED、正式direct OCP probeは依存不足でBLOCKED。実包含・8誤差上界・全状態対応はUNKNOWN、代表実区間はNOT_TESTED。これらを解除しない。
原artifact29 ZIPの保存後再取得・byte/SHA/CRC一致は報告されているが、hidden31欠落、18 ZIPのsource未収録、意味・画像監査未実施を保持する。今回は実ZIPの再監査NOT_TESTED。
Stage3-D-5E原commit `8c8c7dbb33184564e084f0821a0d16b5e3a58af4` は過去の限定探索で未回収。回収BLOCKED、隔離復元NOT_TESTED、提出HOLD/マージNOを維持する。source ZIPや合成Git objectから原commitを再生成して代用しない。
最新取得レビュー（2026-11-18T08:57:51Z）では既存158ファイルの自己再取得照合が報告され、追加保存BLOCKED・追加監査NOT_TESTED。2件の旧stdout欠落はSOURCE_OUTPUT_MISSING。これはPR記録時点の状態であり、現在のWindows live状態の検査ではない。
同レビューは同一Windowsアカウントで保存A・検証Bを分けることを認める。別アカウント不在だけを一律BLOCKEDにする必要はない。ただし実ファイルシステムの書込拒否は実制約であり、規約変更による解消と扱わない。ACL変更・管理者迂回は行わない。

## 成果物単位のリスク分類案（正式適用ではない）
|対象|候補Level|必要な継承条件|
|---|---|---|
|新しい適用説明・合成fixture・Git再取得可能な通常成果物|1|Issue/branch/PR、HEAD追跡、必要CIとレビュー。毎回のArchiveや別アカウントを追加しない|
|非機密の原ログ・原ZIP・復元用bundle|2|承認済保存先への実保存、直接再取得、byte/SHA/適用CRC/manifest。復元が目的なら空bare復元、fsck、全object/refs/祖先・自己完結性を省略しない|
|機密混入・復元不能で高真正性を要する原物・破壊操作|3条件付き|具体的リスク評価と個別安全条件。全リポジトリを一律Level3にしない。別アカウント/VMは案件上必要な場合のみ|
原物未回収はUNKNOWN/BLOCKED、実破損はFAIL、保管先不達はBLOCKEDとして別々に保持。内容一致、来歴、復元、独立性を相互に昇格させない。

## 推奨パイロットと再開条件
中央Stage1-Aの限定技術受入後、既存Issue/PR重複を確認して、mainを基準とする独立した追加専用の文書・合成データパイロットを候補とする。凍結されたPR41積層履歴への混入、workflow変更、原証拠移動、既存不合格の解除は避ける。
1. 最新main・AGENTS・workflow起動条件を再確認し、通常PR CIの実行範囲とnative/browser負荷を導入審査する。
2. 導入対象を新規合成物と記録schemaに限定し、実原物に依存する合格判定を分離する。
3. 旧保全契約を弱めず、SOLO技術監査と人的独立性を別軸で記録する。
4. 原commit回収や重要原物復元を受入条件にする工程は、その証拠が揃うまで停止を維持する。
横断展開方針の包括承認を再要求する提案ではない。リポジトリ固有の副作用・適用範囲審査が必要である。今回は候補調査のみで、本番適用PASSはNOT_TESTED。

## 根拠
- [PR #41](https://github.com/tetsujisugimori-coder/castle-3d-parts/pull/41)
- [5D最終報告](https://github.com/tetsujisugimori-coder/castle-3d-parts/pull/41#issuecomment-6902861205)
- [5E回収報告](https://github.com/tetsujisugimori-coder/castle-3d-parts/pull/41#issuecomment-6933532367)
- [最新取得レビュー](https://github.com/tetsujisugimori-coder/castle-3d-parts/pull/41#pullrequestreview-5953429397)
- [固定版workflow](https://github.com/tetsujisugimori-coder/castle-3d-parts/tree/7b2dceee7e42075bbd03967a139fd48f1fd55624/.github/workflows)
- Actions REST: /repos/tetsujisugimori-coder/castle-3d-parts/actions/runs?head_sha=7b2dceee7e42075bbd03967a139fd48f1fd55624&per_page=100
- Checks REST: /repos/tetsujisugimori-coder/castle-3d-parts/commits/7b2dceee7e42075bbd03967a139fd48f1fd55624/check-runs?per_page=100

判定: 調査PARTIAL。既存CI状態の取得PASS、現在原ZIP/Windows/全外部設定の独立監査NOT_TESTED/UNKNOWN。初期候補として妥当だが、PR41の技術HOLDは維持。公表用本文に内部保存先や非公開IDは収録していない。

