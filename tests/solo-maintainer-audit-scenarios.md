# 単独開発向け監査の合成反例案（未実施）

対象: [v0.1.1補訂案](../docs/solo-maintainer-audit-proposal.md)。**全件 NOT_TESTED、実装済み検査器なし、実保存/再取得なし、Gate permit=false。** 旧AT01〜AT12の合成PASSを本案の回帰PASSへ流用しない。

|ID|モードと入力|提案仕様の期待|監査独立性|
|---|---|---|---|
|SM01|v0.1.1を正式採用し、非機密・低リスク案件に事前承認したSOLO。所有者は同じ、別セッションBが承認保存先から直接取得し原物全byte/ZIP全件検証|技術照合PASS（他ゲートが成立した場合に限る）|LIMITED_SHARED_OWNER。第三者独立監査PASSは禁止|
|SM02|同じ所有者がAのworkspace内コピーだけをB証拠と申告|FAIL / WORKSPACE_COPY|独立取得不成立|
|SM03|Aの自己照合stdoutだけでBの実取得を省略|BLOCKED / DIRECT_RETRIEVAL_MISSING|独立取得不成立|
|SM04|保存物と固定原ZIPのSHA-256または全byteが不一致|FAIL / CONTENT_MISMATCH|独立性以前に停止|
|SM05|ZIP全byte検査を省略、またはmanifestの行/size/SHA/CRCに不一致|NOT_TESTED（未検査）または FAIL（不一致実証）|技術照合PASS不可|
|SM06|元原ZIPの所在がUNKNOWNで再生成した別ZIPを提示|BLOCKED / ORIGINAL_NOT_RECOVERED|新証拠の別版管理が必要|
|SM07|STRICT指定案件でA/Bが同一所有者・同一資格情報|BLOCKED / INDEPENDENT_ACTOR_ABSENT|STRICT独立監査PASS不可|
|SM08|v0.1.1未採用の案件にSOLOを遡及適用|BLOCKED / POLICY_VERSION_NOT_ADOPTED|旧P05を上書きしない|
|SM09|SOLO対象へ機密混入疑い、ACL読取不明、保持設定不明|BLOCKED / SCOPE_OR_STORAGE_UNVERIFIED|転送しない|
|SM10|同一ユーザーで別作業領域・別セッションだが同じ検証器の自己申告結果しかない|BLOCKED / INDEPENDENT_INPUT_NOT_OBSERVED|技術証拠不足|

期待入力schema、固定oracle、正常対照、実行器、故障注入、Windows実機での監査は別途設計・実装・実行が必要。予期したFAILを正しく拒否する試験のPASSと、実証拠の受入PASSを混同しない。
