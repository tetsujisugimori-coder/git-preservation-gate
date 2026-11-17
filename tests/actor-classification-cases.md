# AI実行主体分類と来歴：合成反例仕様12件（未実施）

すべて**NOT_TESTED**。これは設計レビュー用の反例表で、実行済み検査数や保全成功数に算入しない。入力は合成データのみ。検証では分類の期待値とGate許可boolを分けて比較する。正本は[分類](../docs/actor-execution-taxonomy.md)と[レコード契約](../docs/execution-provenance-contract.md)。

|case|合成入力/対照|確認したい判定|現在状態|
|---|---|---|---|
|AT01|Web版ChatGPT、Work指定なしをWORK-CLOUD-WEBと宣言|CHAT-WEBとの区分差を検出。Work実行の証拠欠落で不正分類を拒否|NOT_TESTED|
|AT02|Desktop起動のWork、クラウドワーカー確認ありをWORK-LOCALと宣言|WORK-CLOUD-DESKTOPに分類、local誤認を拒否|NOT_TESTED|
|AT03|Desktop起動のWork、実処理先の観測なしをWORK-LOCALと宣言|local判定UNKNOWN、必須ゲート許可false|NOT_TESTED|
|AT04|Mobile起動のWork、cloud観測ありをWORK-CLOUD-WEBと宣言|WORK-CLOUD-MOBILEとの起動面不一致を検出|NOT_TESTED|
|AT05|同じタスクをCodex local/cloudで実施、execution_id/環境証拠を共用|CODEX-LOCAL/CODEX-CLOUDの別レコード必須、証拠流用拒否|NOT_TESTED|
|AT06|DOTがCodex Cloudへ委任したが子executionなし|委任履歴欠落のためCODEX-CLOUD実行完了を認定しない|NOT_TESTED|
|AT07|DOT→Codex Cloudの子記録あり、委任根拠refなし|parent-child申告だけでは足りず後続許可false|NOT_TESTED|
|AT08|異なるrepoで同名タスクを実施し、一方のOIDを他方へ再利用|repository/commit/tree突合で拒否、別repoを独立PASSとしない|NOT_TESTED|
|AT09|同じprovider・共有workspaceの別actor名で独立審査を申告|名称差だけでは独立PASS不可、共有境界の開示が必要|NOT_TESTED|
|AT10|再試行で元attemptを上書きし、旧FAILを消去|旧票消去と同一attempt再利用を拒否|NOT_TESTED|
|AT11|必須actor/environment証拠が双方欠落し、空一致をPASSと採点|欠測を許可せず状態/理由を分離|NOT_TESTED|
|AT12|生成元と異なる保存先から再取得せず、別パスのworkspaceコピーで監査PASSを申告|P03/P05の実再取得未達。分類PASSでもGate B不可|NOT_TESTED|

## 将来の検証原則
各caseに正常対照、入力票、期待分類、期待停止、実際の検査原票、exit/例外、証拠参照、担当を追加したうえで実行する。評価用validatorと同じ実装から期待値を生成しない。ラベルが合っても実環境の独立性・保存先実取得・隔離復元が成立したとは扱わない。ケースをひとつ実施しても未実施11件をPASSへ換算しない。
