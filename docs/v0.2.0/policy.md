# 中央保全・監査統合規約 v0.2.0 案

**DESIGN_PROPOSED / Stage 0のみ。未採用。** 正本v0.1.0を変更しない。PR #4のv0.1.1は未採用案であり本案の設計入力。文書受入・規約採用・案件適用・Stage 1実運用・マージは別判断。本案の合成試験は実保存や強制ゲートの証明ではない。

## 1. 原則と対象固定
取得済み原物の喪失防止を優先する。リポジトリ全体でなく、成果物・証拠・操作ごとに分類し、同じPRの通常文書と重要原ZIPを別票にする。対象ID、repository、完全HEAD/tree/parents、参照ref、規約version/commit、案件契約、分類理由、監査方式を開始前に固定。旧原票と失敗履歴は追記で保持する。結果を見た後のレベル引下げや方式変更で失敗を隠さない。

## 2. 3段階分類
|Level|対象・判断根拠|必須|一律には要求しない|
|---|---|---|---|
|1 通常保全|公開・再取得可能な通常コード、文書、Issue/PR。機密・重要な実測証拠ではない|Git/変更管理、HEAD/履歴、案件別CI・レビュー|Archiveコピー、個別承認票、A/B分離、ZIP、別account、VM|
|2 重要証拠|非機密の実験原票・原ZIP・再生成困難な結果・将来監査の入力|承認永続先への実保存、receipt、直接再取得、size/SHA-256、重要原物全byte、適用wrapper検査|別人/別account/VMの一律義務|
|3 特別保全|機密、復元不能原本、重大破壊リスク、強真正性・改ざん耐性|個別承認、分類とACL、保存・再取得・内容照合、リスク別追加安全条件|無関係な強化策の一律義務|

分類票は機密性、再生成可能性、喪失影響、変更/破壊影響、公開範囲、監査/復元必要性を記す。機密疑いも低レベルに推定せず転送停止。L2原ZIPは別の再生成物で代用不可。L3の独立主体・VM等はリスク評価と案件契約で選び、必要項目は事前固定する。分類不能はUNKNOWNで危険な転送・破壊を停止し、読み取りや安全な文書整理は継続可能。

## 3. 四状態と集約
- CUSTODY_STATUS: 原物の保存。承認範囲、保存先適合、保存版receiptを根拠にする。
- VERIFICATION_STATUS: 保存先の実物再取得と必要な内容照合。
- INDEPENDENCE_STATUS: 人、資格情報、session、execution、host、workspace、取得経路、検査器、履歴の共有を個別記録。
- ACCEPTANCE_STATUS: 対象成果物の必要検査・CI・レビュー・権限を含む受入判断。

検査状態PASS/FAIL/PARTIAL/BLOCKED/UNKNOWN/NOT_TESTEDの意味はv0.1.0 P06を維持。適用有無は別boolと理由で固定し、非適用をPASSに変更しない。検査群はFAIL優先、次にBLOCKED、全PASSのみPASS、非PASSが単一種ならその状態、混合ならPARTIAL。受入は必須FAILならFAIL、阻害ならBLOCKED、他の必須非PASSならPARTIAL。SOLOの独立性はLIMITED_SHARED_OWNERとして別に保持し、契約で許す技術監査要件だけ満たせる。人的独立性PASSではない。

L1の追加archive custody/verification/independenceはNOT_TESTED・非適用。これはGit履歴の確認を省略する意味ではない。L2保存PASS・再取得未実施は検証NOT_TESTED、受入PARTIAL、B/C不可。失敗は対象ごとに集約し、無関係な安全な文書作業へ停止を伝播させない。

## 4. 原物検査と限界
実保存版のreceipt、取得時刻/経路、実size/SHA、比較対象の原bytesを固定する。重要原物は全byte比較。原bytesが不在なら全byte NOT_TESTED/UNKNOWNであり、hash文字列比較だけで代用しない。ZIPは全entry CRC、重複名・危険path、manifest集合/size/hashを検査する。manifest未存在は完全性UNKNOWN/必要契約未達であり空同士一致は不可。ZIPでない物にCRCを要求しない。

Git bundleの自己完結性/復元が目的の案件はv0.1.0 P01/P02/P04を維持。prerequisite、shallow、partial、alternates依存を確認し、空bare復元・fsck・raw OID・tree/parents/ref集合・全blobを照合。Level 2やSOLOを理由に省略しない。非Git/LFS/submodule等は別対象として必要性を固定。暗黙にbundle収録済みとしない。

## 5. 実運用採用ゲート
本案・合成器は本番の許可を発行しない。合成gate_eligibilityと実permitを別出力とし、Stage 0 permitは常にfalse。実運用には版採用、対象ごとの契約、実データ取得手順/期限/停止方式、権限、独立設計レビューが必要。規約更新は自動配布しない。他案件の旧FAIL/BLOCKEDを変更しない。

分類UNKNOWNは既知の矛盾を隠す理由ではない。機密=true等で最低Level3が確定するのにLevel1/2を申告したらFAIL。分類未確定でも、実証されたSHA/CRC等のFAILは対応する保存/検証軸に保持し、受入をFAILにする。未分類だから全てUNKNOWNへ巻き戻さない。
