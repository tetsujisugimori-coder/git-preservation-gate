# Gate A/B/C契約（v0.1.0参照）

正本は[規約](preservation-policy.md)。以下は将来の入出力仕様で、現在の検査実装ではない。

## 共通
入力の必須field、型、非空集合、対象版、証拠参照と実bytesを検査する。欠落を空同士一致で通さない。schema不正はFAIL、権限不足はBLOCKED、timeoutはUNKNOWN。全工程の期限・cleanup予算・容量・retry上限を開始前に固定し、期限超過後に処理を放置しない設計とする。具体値とOS別停止方式はStage1の試験計画で決めるまでBLOCKED。非Git資産が必要ならP08追加契約も必須。

|ゲート|入力/前提|担当|出力|成功条件|停止する操作|再実行条件|
|---|---|---|---|---|---|---|
|A commit直後|固定OID/tree/parents/refs、承認対象集合、Git版/環境、非Git棚卸し|生成担当|target票、自己完結bundle、manifest、生成/verifyログ|P01/P02、元全object整合、prerequisiteなし、対象変化なし|保全済み宣言、元環境の意図的破棄・次の破壊的操作|原因解消・同一対象再固定、新attempt。対象変更はAから|
|B 作業終了前|A PASS、保存先承認/容量/アクセス、独立担当|保存担当＋独立取得/復元担当|保存版receipt、再取得物、空bare復元ログ、全照合、独立監査|P03/P04/P05、必要非Git追加契約、全必須PASS|安全引渡し完了・保全完了宣言、意図的cleanup/終了許可|失敗原票保持、保存版固定、承認/権限・原因解消後。旧環境消失は回復別工程|
|C PR受入前|B PASS、PR提出HEAD/tree、採用規約commit、レビュー対象版、製品CI契約|受入責任者＋独立reviewer|受入判定票/permit、必要時承認要求|提出HEAD=B対象=レビュー対象、証拠整合、required/製品受入CI結果充足、未解決阻害なし|merge/受入完了扱い|新HEADならA/B/Cやり直し、同HEAD新証拠はB/C再審査|

Gate Cは「CIなし」を成功にしない。文書案件など事前承認されたCI不要契約なら `not_applicable` 理由を独立レビューする。検査状態としてのNOT_TESTEDをPASSに変換せず、受入対象から除外した契約を明示する。WebKitだけを全案件の絶対条件にせず、製品ごとに固定された既存受入条件を継承する。

## 固定とTOCTOU
A入力時、生成完了時、B開始/終了、C直前にref/targetを照合。対象が変化すれば旧票は旧OIDに有効でも新OIDには無効。C判定後merge直前のexpected HEAD一致が必要。監査中の差替えはdigest不一致として拒否。完全な排他は採用先の仕組みに依存しUNKNOWNのままでは強制保証しない。

## 検査分解
A01対象/schema、A02対象履歴・到達object、A03生成exit・bundle前提、A04 bundle verify。
B01承認/保存receipt、B02実取得、B03size/SHA/全byte・wrapper検査、B04空隔離前提、B05復元/fsck、B06rawOID/tree/parents/ref名集合・ref→OID/path/mode/blob/集合、B07独立監査/必要追加資産。
C01版一致、C02証拠の完全性、C03案件別CI・review・未解決指摘、C04権限/明示承認。
それぞれ個別結果と理由コード・証拠を持ち、集計はP06に従う。

## 強制力の限界
|層|止め得るもの|限界|
|AI作業依頼/AGENTS|手順上の完了宣言・提出判断|無視や突然の環境破棄を技術阻止できない|
|ローカルhook/CLI wrapper|導入済み経路での操作|bypass、別client、未導入repoに無効|
|CI check|CI上の検査合否|未push成果・環境の消失を保護しない。trusted evidence取得も別問題|
|GitHub required check/protection|設定と対象branchに応じたmerge|管理者bypass・設定変更権限・適用範囲を検証する必要。未設定で強制とは言わない|
|保管サービス|保存済み版の保持/アクセス|期限、削除権、障害。実測取得と保持保証は別|

Stage2の導入審査で適用範囲/検査主体/回避可能性を観測し、機械検査成功と強制力実証を別判定する。Gatesはpush許可を自動発行せず、元案件の停止条件を解除しない。
