# AI実行主体分類と来歴の合成反例12件

正本は[分類](../docs/actor-execution-taxonomy.md)と[レコード契約](../docs/execution-provenance-contract.md)。下表の検査はStage 0専用で、実運用の観測、保全・復元、独立監査の成立を証明する試験はNOT_TESTED。Gate A/B/Cのpermitはすべてfalse。

## 固定入力と期待出力
- [入力fixture](stage0-actor/fixtures.json)は各ATに正常対照 `normal` と故障注入 `fault` を持つ。作業主張 `records` と証拠票 `evidence` を別入力とし、必要なケースは委任票・旧台帳・監査票も与える。監査票の申告と観測した担当者ID・共有要素・承認対象・保存先からの取得票は別入力にする。
- [事前期待値](stage0-actor/oracle.json)は次の5項目を固定する。`classifications` はrecord_idから分類（分類不能はnull）への写像、`input_status` は合成入力全体、`reason_codes` は重複のない辞書順の理由、`audit_status` は合成監査票の入力判定、`permit` はA/B/Cの各bool。入力の違反を期待どおりFAILにしたときは試験実行PASS。入力証拠が矛盾ならFAIL、必須前提の欠落ならBLOCKED、観測を試みて判定に足りないときはUNKNOWN。
- 必須の観測票はactorと実処理先、対象のrepository/commit/tree/executionの結び付きを含む。各故障で改変・除去する入力と、追加で必要な票は下表のとおり。

| ケース | 正常対照 | 故障注入 | 故障時の入力判定・理由 |
|---|---|---|---|
| AT01 | 一般ChatGPTのWeb観測 | Work Cloud Webと申告 | FAIL / ACTOR_CONTRADICTION |
| AT02 | Desktop起動のWorkとcloud観測 | Work Localと申告 | FAIL / ACTOR_CONTRADICTION |
| AT03 | Desktop起動のWorkとlocalの観測 | 実処理先を観測不能にする | UNKNOWN / EXECUTION_SITE_UNOBSERVED |
| AT04 | Mobile起動のWorkとcloud観測 | Work Cloud Webと申告 | FAIL / ACTOR_CONTRADICTION |
| AT05 | Codex LocalとCloudに別実行・観測票 | 同じexecution IDとLocalの観測票を再利用 | FAIL / DUPLICATE_EXECUTION_ID, OBSERVATION_MISMATCH |
| AT06 | DOTの委任票、Codex Cloud子実行、親子証拠 | 子実行と対応証拠を欠落させる | BLOCKED / DELEGATED_CHILD_MISSING |
| AT07 | 両実行と親子を結ぶ委任証拠 | 親子の申告を残し委任証拠を除く | BLOCKED / HANDOFF_EVIDENCE_MISSING |
| AT08 | 別repoの同一commit/tree OID、各repo固有の票 | 一方の証拠を別repoに結び付ける | FAIL / EVIDENCE_TARGET_MISMATCH |
| AT09 | 共有基盤を開示した別担当、承認先再取得経路、別検証先の合成監査票 | 監査者を生成者と同一にする（表示名は別） | FAIL / SAME_RESPONSIBLE_ACTOR |
| AT10 | 旧FAIL票と新attempt、元attempt参照 | 旧FAIL票を消し元attemptを再利用 | FAIL / PRIOR_RECORD_REMOVED_OR_CHANGED, RETRY_ATTEMPT_REUSED |
| AT11 | 非空のactor・environmentの観測票 | 両方の証拠を空・欠落にする | BLOCKED / ACTOR_EVIDENCE_MISSING, ENVIRONMENT_EVIDENCE_MISSING |
| AT12 | 承認先から再取得した経路と別検証先の合成監査票 | workspaceコピーを再取得として申告 | FAIL / WORKSPACE_COPY |

## 実行方法
Python 3.10以降の標準ライブラリで `python -I tests/stage0-actor/run.py --log <未作成のログパス>` を実行する。各入力を別processで検査し、exitが0かつstderrが空で、stdoutのJSONが期待値と完全一致した場合に試験PASS。例外、期限超過、未到達も記録対象とし、分母はAT正常12＋故障12。入力と期待値のケース・派生形を開始前に全件照合し、欠落・不一致時はAT24実行をNOT_TESTEDとして記録する。台帳、参照先、独立監査票、receiptの追加対照は別集計とする。期待値は検査器から生成せずに事前記述し、ログに入力・期待・実出力・標準出力・標準エラー・例外・終了状態・時刻・環境・試験ファイルhashを残す。合成監査票の「再取得経路」「別検証先」は入力条件を表す。実際の取得や隔離復元を実行するには、承認と独立担当による別工程を要する。
