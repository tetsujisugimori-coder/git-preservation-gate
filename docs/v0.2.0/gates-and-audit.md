# Gate A/B/C・監査契約 v0.2.0案

正本候補は[policy](policy.md)。現行v0.1.0のゲート実装を変更するものではない。

|Gate|Level 1|Level 2/3|止める範囲|
|---|---|---|---|
|A 対象固定|Git追跡、branch/PR変更管理、対象HEAD|左記＋原物同定、必要なら完全bundle生成と対象集合|対象不明の受入/危険操作|
|B 保全検証|追加archiveは非適用（NOT_TESTED、理由固定）|A＋custody＋verification＋監査方式要件＋リスク追加条件|保全完了宣言、原物廃棄、該当証拠依存の受入|
|C 成果物受入|A、必要CI、レビュー、権限・対象一致|B、必要CI、レビュー、権限・対象一致|該当PR/成果物の正式受入|

C成立はpush/mergeの承認を自動作成しない。CIが0件ならNOT_TESTED。CI不要契約は理由と適用範囲を事前固定し、テストPASSへ変更しない。案件固有の必須CI、安全条件、未解決P1/P2を省略しない。mixed PRは各成果物と依存関係を列挙し、受入必須対象が未成立なら全体受入しないが、独立な安全な作業の継続は可能。

対象HEADや保存版が変化したら別attemptとし、旧結果を保持。C直前と実操作直前にexpected HEADを再確認。失敗後の必須項目削除・SOLOへの暗黙変更は禁止。

## SOLO_STANDARD
同じ所有者・Windows accountでも可。A保存とB検証は別session、別execution ID、別検証領域、保存先から直接取得する別取得操作。AのworkspaceコピーやstdoutだけをB証拠にしない。Bは実bytesを読み、固定原物とsize/SHA/全byte・適用ZIP/bundle検査を実行。共有された検査器を使用した事実も記録し、その証拠の真正性は自己申告で証明しない。

技術照合PASSは可、人的独立性はLIMITED_SHARED_OWNER。資格情報や同一hostの独立性を偽らない。別accountやVMは追加契約が要求した場合のみ。L3で使用できるかは追加安全契約による。レベルだけで人の分離を自動免除しない。

## STRICT_INDEPENDENT
案件契約が要求する独立責任主体・環境分離を実証。主体、権限、共有要素、取得経路、検査入力を記録。別名称・別AI・別processだけで別人としない。人的独立性の証拠不足UNKNOWN、既知の同一主体で要件未達ならBLOCKED。資格情報分離などを要求する契約なら同様に別検査。技術整合PASSと独立性の不足は併記。

## 制御策の強制力
文書/合成器は本番操作の技術的遮断ではない。ローカルhook、CI、branch protection、ACLの導入・回避可能性はStage 1/2で別評価。本案から第三者認証・不変保存・時刻真正性を主張しない。

## P2補訂の機械入力契約
optional `risk_contract` は `{decision, rationale, approval, risks}`。decisionは `required / not_required / UNKNOWN`、approvalは `PASS / FAIL / UNKNOWN / NOT_TESTED`、risksはtrueとなったrisk keyの集合。型・未知key・重複・非該当riskはschema拒否。L3で未提供、UNKNOWN、空白理由、全risk未網羅、requiredなのに必須追加検査が空、not_requiredなのに必須追加検査ありの場合は `RISK_CONTRACT_UNKNOWN`。承認の非PASSは別理由コードで保持し、verificationへ集約する。空理由はschema異常ではなく根拠不足UNKNOWN。

Gate Aの対象同定と、追加安全契約を必要とするB/Cを分ける。正しく承認されたnot_requiredなら基本検査だけでB/Cの合成eligibleは可能。requiredなら従来のextra_checksを全て検査する。低すぎる分類は全eligible=false、acceptance FAIL。保存/検証の既知FAILだけ対応軸に保持し、それ以外はUNKNOWN。Stage 0の実permitは全ケースfalse。

## 分類違反時の既知独立性不成立（追加補訂）
分類が過小または未確定でも、別session・別execution・別workspace・保存先からの直接取得・独立照合入力の必須技術要素が `false` と観測済みなら、`INDEPENDENCE_STATUS=BLOCKED` と対応する `*_MISSING` 理由を保持する。STRICT方式で人的独立性が `false` と確認済みの場合も同様に `HUMAN_INDEPENDENT_MISSING` を保持する。未確認（`null`）はUNKNOWNのまま、分類不成立から独立性PASSを推定しない。SOLO方式の同一所有者・同一資格情報だけを理由としてBLOCKEDにしない。これは合成入力の判定規則であり、実人員・実権限の証明ではない。
