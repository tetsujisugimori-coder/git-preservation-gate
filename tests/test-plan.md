# Stage 1以降の試験台帳（Stage0仕様）

全ケースは **NOT_TESTED**。仕様完成を試験PASSとしない。合成repo・非秘密markerのみを使い、実案件objectを破壊しない。実行前にfixture版、Git/OS、期限・容量・retry上限、承認範囲を固定する。case内に複数注入がある場合は独立subcaseとして全件を事前登録し、都合の良い一件で代表させない。

判定正本: [中央規約P06](../docs/preservation-policy.md)。検査器の「期待した拒否を確認した試験PASS」と、入力bundleの保全判定FAIL/BLOCKEDは別欄に記録する。未実装のため今回は実値欄なし。

|試験ID|目的|前提|入力|故障注入|期待する保全判定/観測|停止すべき処理|必要証拠|実施Stage|現在状態|
|---|---|---|---|---|---|---|---|---|---|
|T01|正常commit|全履歴合成repo/承認済み先/独立者|固定refと全到達集合|なし|全必須PASS、A/B許可|なし|生成/verify/保存receipt/再取得/空bare/fsck/object/独立票|1|NOT_TESTED|
|T02|未push commit|remoteより1commit先、正常前提|未push完全OID|remoteを更新せず保全|T01同様PASS、未pushでも復元一致|なし、push不要|T01証拠＋remoteとlocalの差|1|NOT_TESTED|
|T03|必要object欠落|合成repoのみ|対象blobを欠く複製DB|複製中の必要objectを除去|A02 FAIL、または生成失敗FAIL。未到達検査NOT_TESTED|保存成功宣言/B/C|欠落OID/生成exit/fsck/未実施一覧|1|NOT_TESTED|
|T04|前提object付きbundle|incremental fixture|prerequisiteありbundle|一部祖先を除外して作成|A03 FAIL、初版自己完結契約拒否|B/C|bundle header/verify/空bareでの不足記録|1|NOT_TESTED|
|T05|bundle1byte改変|正常bundle複製|原bundleと複製|転送用複製のpack領域1byte反転|B03 FAIL、後段成功へ上書き不可|復元受入/C|変更offset/前後hash/size/比較|1|NOT_TESTED|
|T06|SHA不一致|正しい原bytes|manifest|期待SHAの1文字を改変|B03 FAIL|B/C|manifest差分/再計算値|1|NOT_TESTED|
|T07|書込み拒否|専用合成保存先|正常bundle|保存アダプターが権限拒否|B01 BLOCKED、再取得NOT_TESTED|保全完了/終了許可|拒否receipt/exit/権限範囲|1|NOT_TESTED|
|T08|再取得不能|保存済み合成版|固定保存版|GET拒否または不存在を模擬|B02 BLOCKED、保存成功と別|B/C|保存receipt/取得エラー/試行|1|NOT_TESTED|
|T09|復元汚染|復元先は事前object入り|正常bundle|事前DB/object pool/alternatesを置く|B04 FAIL、空環境と称さない|復元認定/C|復元前一覧/env/config|1|NOT_TESTED|
|T10|commit一致・tree申告不一致|正常commitを保持|manifestの期待tree|別tree OIDを申告|B06 FAIL（暗号衝突を生成する試験ではない）|B/C|raw commitのtree/申告/差分|1|NOT_TESTED|
|T11|parent不一致|2parent合成merge/rootも別fixture|ordered parents|parent削除/順序入替/追加|B06 FAIL|B/C|raw parents全配列/期待|1|NOT_TESTED|
|T12|途中HEAD変更|固定後の合成ref|target票|A生成後またはB/C境界でrefを前進|対象一致FAIL、新attempt必要|旧票での新HEAD受入|前後ref/時刻/旧票|1|NOT_TESTED|
|T13|監査証拠欠落|正常結果票複製|必須証拠参照|空配列/欠落/両側欠落|schema FAIL、許可false|B/C|欠落field/診断/非空case集合|1|NOT_TESTED|
|T14|独立担当不在|自己検査完了|review identity|同一担当/未割当のみ|B07 BLOCKED、自己PASS保持|B/C|担当分離記録/制約|1|NOT_TESTED|
|T15|秘密混入|機密ではないmarker合成履歴|過去commitにsecret marker|HEADでは消したmarkerを祖先に置く|機密リスクBLOCKED、公開/転送停止|保存先未承認の転送/公開|非秘密marker位置/分類結果|1|NOT_TESTED|
|T16|環境消失|使い捨て合成sandbox|A完了/B未完票|制御された試験sandboxを終了|B BLOCKED、失われた分UNKNOWN/NOT_TESTED、PASS禁止|完了宣言|消失時点/残存証拠/復旧可能範囲|1|NOT_TESTED|
|T17|復旧後再試行|T08の失敗票保持|同一保存版/新attempt|一時拒否解除、別path再取得|旧BLOCKED保持、新attempt全検査後だけPASS可|旧証拠上書き|旧新attemptと版一致/新全証拠|1|NOT_TESTED|
|T18|AI規約不遵守|合成採用repoと未導入client|証拠なし完了要求|AGENTS未読/古い版/ゲート迂回|採用CI/保護の範囲で拒否。未導入経路は強制UNKNOWN/FAIL|受入、ただし環境破棄阻止と称さない|経路別操作/設定/bypass結果|2（Stage1では契約mockのみ）|NOT_TESTED|
|T19|未commit/外部資産|Git以外の必要資産あり|dirty/index/untracked/LFS/submodule一覧|bundleだけ提出|追加契約未達BLOCKED、Gitだけ成功はPARTIAL|B/C|棚卸し/除外承認または不足一覧|1|NOT_TESTED|
|T20|浅い/partial/replace依存|合成制限repo|bundle候補|shallow/promisor/replace/graftを各別fixture|A前提BLOCKED、必要object欠損実証時FAIL|生成の受入/B/C|設定/対象履歴/欠損/未到達|1|NOT_TESTED|
|T21|復元失敗|正常再取得と空bare|restore処理|書込拒否または壊れた入力を各別fixture|権限BLOCKED/破損FAIL、B05非PASS|B/C|restore exit/stderr/入力hash|1|NOT_TESTED|
|T22|期限/権限/容量|事前に上限固定した合成環境|生成/保存/監査の各操作|停止・容量不足・権限拒否を各別fixture|timeout UNKNOWN、前提不足BLOCKED、全許可false|完了/次操作|期限/cleanup/process残留/容量/原票|1|NOT_TESTED|
|T23|規約版の無承認更新|旧版採用fixture|新規約commit|latest参照/未承認版で検査|C01 FAILまたは未設定BLOCKED|C/自動展開|採用版/実行版/承認比較|2（Stage1では契約mockのみ）|NOT_TESTED|
|T24|提出対象相違|B済みの合成commit|PR HEAD|Bと別HEADのPRへ票添付|C01 FAIL|merge受入|GitHub HEAD/B対象/レビュー対象|1|NOT_TESTED|
|T25|証拠改変/危険wrapper|合成証拠ZIP|manifestとentry|重複名/path traversal/extra/missing/byte改変を各別fixture|B03/schema FAIL、展開前停止|展開/B/C|安全一覧/集合差/hash/CRC|1|NOT_TESTED|

## 正常・負例の実施規則
正常T01/T02の全保全経路を実測し、拒否だけの検査器を成功にしない。負例は同一入力の正常対照を保持し、一因子を改変する。起動不能や未到達はNOT_TESTED/BLOCKEDを残す。集計には固定case/subcase集合と全分母を含める。正常の期待は入力保全PASS、負例の期待は入力拒否であり、両者を同じ成功数へ無説明に足さない。

T10は同一commitから異なるtreeが生じると仮定せず、対象票の不一致検出を試す。T11はroot/単parent/mergeの順序と個数を扱う。T17でも失敗履歴を消さず、新attemptだけの結果を採点する。T16は消失を防げるかではなく、残存証拠から保全未成立を誤認しないかを試す。

## 検査器自身の受入
schemaの必須型、case集合、非空入力、参照先size/hash、対象OID、permit集計、旧票流用拒否を反例で確認する。検査器実装の同じ関数からoracleを生成しない。実装担当とは別の監査担当がfixtureと期待値を読む。Stage1以降の実行では失敗票も保存し、再取得と独立復元の結果を別々に残す。
