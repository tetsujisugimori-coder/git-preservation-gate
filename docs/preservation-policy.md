# 中央保全規約 v0.1.0（Stage 0提案版）

## 正本・境界
この文書を規範の正本とする。関連文書は具体化であり衝突時は受入を停止し改訂審査する。MUST相当の「必須」は将来実装の契約であって、現在強制できるとの主張ではない。規約採用・Stage1開始・他repo適用には別承認が必要。

## P01 対象固定
案件ID、repository、object format、完全commit OID、tree OID、順序付き全parent OID（rootは空配列）、採用ref→OID、規約版と採用commitを固定する。到達可能な全commit/tree/blob/tag（選択refがtagを指す場合そのtag objectを含む）を必要集合とする。選択refの集合自体も承認し、無関係なrefを無差別収録しない。未push commitも同じ扱い。HEADの再読取が途中で変われば当該試行を停止し、新対象・新試行へ分離する。旧証拠は上書きしない。

## P02 自己完結bundle契約
初版は前提objectなしの完全履歴bundleのみ。incremental/prerequisite、shallow、partial/promisor、欠損、replace/graftによる見掛けの履歴、alternates依存を受入れない。shallow等の非対応構成・依存制約はBLOCKEDとして別回復工程へ。必要objectの欠損・破損を実証した場合はFAILとし、制約による未確認と区別する。対象refと全到達集合を記録し、bundle生成成功、bundle verify、空bareへの復元、fsck、元objectとの照合を別結果にする。単にhashが記録に残るだけでは復元可能性を証明しない。報告値からcommitを作り直して代用してはいけない。

## P03 保存と再取得
承認記録で案件・データ分類・保存先・主体・操作・保持目的を特定する。保存成功receiptと保存版を固定し、別pathへ保存先から実bytesを取得する。workspaceコピーは再取得ではない。生成前後ではなく、生成済み原bundleと保存後再取得物のsize/SHA-256/全byteを比較する。ZIP等のwrapperがあればCRCとmanifest全件を追加検査するが、Git bundle自体にZIP CRCを要求しない。CRCは真正性を保証しない。

## P04 隔離復元
新規の空bare repositoryで、ネットワーク・代替object・共有object pool・事前ref・Git環境override・template hooks・外部filterに依存せず復元する。Git版・OS・コマンド・開始終了・exit・stderr/stdout・環境除外条件を記録。checkoutやコード実行は不要。復元前に空DBを検査、復元後にfsck full/strict、raw object内容からOID再計算、commitのtree/全parent、承認済みref名の集合とref→OID対応（余分・欠落も拒否）、全到達集合（型・size・OID）、treeのpath/mode/blob bytesを元固定記録と照合する。Git formatの違いは同一OID比較不可として停止し、暗黙変換しない。

## P05 独立監査
生成・保存担当と異なるレビュー担当を記録。監査者が保存先から自ら再取得し、空の別復元先でP03/P04を確認する。producerログを読むだけ、同一担当の別processだけでは独立PASSにしない。同一基盤・共有workspace・共通モデル・履歴継承は限界として開示。監査対象を固定し生成担当による監査出力の変更を避ける。権限分離/署名等が未実装なら耐改ざん保証UNKNOWN。独立者不在はBLOCKED。

## P06 判定
|状態|意味|
|---|---|
|PASS|指定対象・範囲・版の必須検査が実施され期待を満たす|
|FAIL|不一致/破損/規約違反など矛盾を実証|
|PARTIAL|一部の成立のみ。必須欠測を含み全体許可ではない|
|BLOCKED|権限・環境・前提・独立者不足で必要工程に進めない|
|NOT_TESTED|実行していない|
|UNKNOWN|試みたが証拠不足で結論不能|

状態は検査ごとに保持する。全体は必須にFAILならFAIL、FAILなしで阻害ならBLOCKED、それ以外に必須非PASSがあればPARTIAL、全必須PASSのみPASS。UNKNOWN/NOT_TESTEDをPASSへ丸めない。Gate A/B/Cの許可boolはそれぞれ必須全PASSの場合のみtrue。任意チェックの非実施は事前に任意と固定されたものだけ許容し、結果を見て任意化しない。

## P07 完了・例外
保全完了とはGate B必須が全PASSで監査記録が固定された状態。PR受入はさらにGate C全PASSが必要。Gate Aだけの成功、bundle verifyだけ、SHA一致だけ、復元だけを代用しない。保存先不達・監査欠落なら作業の「安全な引渡し完了」を禁止し、途中報告と承認済み保全救済のみ許す。環境突然消失を阻止できず、Gate A前やB未完の成果は失われ得る。

再試行は新attemptで原因・旧結果・入力同一性を記録。通信一時故障の上限/期限は実行前に案件契約へ固定、未知のまま自動再試行しない。破損・情報漏えい疑い・HEAD変更では自動再試行禁止。新対象や保存先変更は再承認。例外承認はリスク引受でありPASSや不足証拠の代替ではない。例外を別結果として記録し、保全済みと呼ばない。

## P08 非Git資産
未commit/index差分、未追跡・ignored、生成物、Git LFS実体、submodule別repo、外部依存はbundleで保全したと扱わない。対象一覧と機密分類を作り、必要なら別の承認済みアーカイブ/manifest/再取得/独立照合契約を必須追加する。初版でその契約がない必要資産がある案件はBLOCKED。不要な資産は理由付き除外を事前承認する。Git設定・hooks・reflogもbundle保全対象外で、必要性を同様に判定する。

## P09 権限
PR提出の承認とマージの承認は別。保全PASSはpush/公開/マージの許可を創出しない。秘密混入疑いは転送/公開停止、機密原本を公開ログに貼らない。中央規約改訂もbranch/PR/独立レビュー/所有者判断を経て採用版を更新する。[適用計画](ai-integration-plan.md)と[保存契約](security-and-storage.md)を参照。
