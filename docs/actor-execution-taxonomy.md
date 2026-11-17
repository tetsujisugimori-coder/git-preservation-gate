# AI実行主体・起動面・実行環境の分類（Stage 0補訂、設計仕様）

## 適用境界
本書は[中央保全規約v0.1.0](preservation-policy.md)と[AI適用計画](ai-integration-plan.md)を補足する**定義案**である。分類表を設けることはGate A/B/Cの実装・稼働・強制を意味しない。実運用へ採用するにはStage 1/2で別途承認・実測・独立審査が必要。名称や提供機能は変わり得るため、観測された実行経路を優先し、推測はUNKNOWNとする。

## 分けて記録する五つの軸
1. **担当上の主体**（`actor_kind`）: どのAI/クライアント区分として作業を受けたか。分類と本人確認は別。
2. **起動面**（`client_surface`）: web / desktop / mobile / cli / api / automation / other / unknown。操作した端末を示すだけで処理場所ではない。
3. **実処理先**（`execution_site`）: cloud / local / hybrid / unknown。観測できたワーカー/プロセスを根拠に記録し、見えていない部分はunknown。
4. **実行主体の来歴**（`execution_id` / `parent_execution_id`）: 指示発行元、実行先、委任、試行を別イベントで結ぶ。同一人物・同一UIでも実行は分離。
5. **権限・信頼境界**（`authority_scope` / `environment_evidence`）: 読取・書込権限、Git/保存先アクセス、環境分離、証拠取得を実測で説明する。

`actor_kind`の名称のみでは、Gitへの書込権限、保存先への到達、ローカル処理、独立監査、同一性を証明しない。UIとワーカーが複数のときは実行イベントごとに記録する。

## 10区分（分類名を固定）
|actor_kind|区分|記録上の要点|
|---|---|---|
|CHAT-WEB|ChatGPTのWeb利用|Web UIからの対話。ローカル作業環境と誤認しない|
|CHAT-DESKTOP|ChatGPTデスクトップ利用|Desktopアプリ経由。ローカルファイルにアクセスできても推論/実処理先は別に観測|
|CHAT-MOBILE|ChatGPTモバイル利用|Mobile経由。端末上で保全処理が走ったとの推定は禁止|
|WORK-CLOUD-WEB|ChatGPT Work、Web起動のクラウド処理|起動面web、実処理先cloudを**それぞれ確認**した場合のみ|
|WORK-CLOUD-DESKTOP|ChatGPT Work、Desktop起動のクラウド処理|起動面desktop、実処理先cloudを別確認|
|WORK-CLOUD-MOBILE|ChatGPT Work、Mobile起動のクラウド処理|起動面mobile、実処理先cloudを別確認|
|WORK-LOCAL|ChatGPT Workのローカル実行経路|実際のローカルワーカーを検証した場合のみ。Desktop起動だけでは該当しない|
|CODEX-LOCAL|ローカルCodex CLI等|Git/OSが動作するホストの実測が必要。Cloudと同一セッション扱いしない|
|CODEX-CLOUD|Codexのクラウド実行|クラウドワーカー・作業領域・Git対象を独立して固定|
|DOT|dot型エージェント（例：八兵衛）|調整・指示・委任する主体。委任先実行をDOTの自己実行として代用しない|

これは製品機能の可用性を保証する一覧ではなく、**実際に確認できた経路を分類するための語彙**である。対象外サービスや実行先が分からない経路を、見た目が近い既知区分へ押し込まない。未知の分類は分類規約の改訂審査に回す。

## 決定手順
1. 実際に操作/開始したUIを証拠とともに固定し、`client_surface`を決める。起動面不明ならunknownを保持。
2. Work / Codex / DOT / 一般ChatGPTのどの処理に属するか、タスク/セッション記録と実行ログから判定する。自己申告だけなら確認不足。
3. プロセス、実行ワーカー、作業領域の根拠から`execution_site`を判定する。端末OS名だけを根拠にしない。
4. `actor_kind`との整合性をチェックする。Workクラウドの三分類には対応する起動面とcloud観測を必要とする。WORK-LOCALにはlocal観測を必要とする。
5. 委任・中継・別担当への引継ぎがあれば、別`execution_id`と親子関係・委任の根拠を登録する。失敗/再試行は新`attempt_id`で保持する。
6. 個別のGate A/B/Cでは[来歴記録契約](execution-provenance-contract.md)と対象Git版/証拠を照合する。欠測を便宜的なPASSに変えない。

## 代表的な区別
- **DesktopからWorkを起動**: 起動面desktopでも、cloudワーカーなら`WORK-CLOUD-DESKTOP`。localと断定しない。
- **WebからWorkを起動**: cloud処理実測なら`WORK-CLOUD-WEB`。同じWorkでも前項と起動面が違う。
- **八兵衛からCodex Cloudへ依頼**: DOTの指示記録とCODEX-CLOUDの実行記録を分離。parent-childで結び、操作主体をすり替えない。
- **Codex CLIとCodex Cloudが同じIssueを担当**: 同一タスク名でも別`execution_id`・作業領域・Git HEAD・試行。ローカルの証拠をクラウドの証拠に流用しない。
- **別repoで同じ課題を検証**: 研究上は可。ただし`repository`、完全commit/tree、入力fixture、試行をそれぞれ固定。別repoという事実だけで独立性・同一入力・同一結果を認定しない。
- **WorkのCloudとLocalを切替**: 移行/委任を別イベントとして記録し、双方の境界の検証ができなければ環境同一性はUNKNOWN。

## 独立レビューとの関係
実装担当・証拠生成担当・独立監査担当は`actor_kind`、実行インスタンス、資格情報、workspace、証拠アクセス経路をそれぞれ記録する。別名称/別モデル/別repo/別UIだけでは独立PASSとはしない。独立監査者が承認保存先から実物を自ら再取得し、空の隔離環境で検証するというP03〜P05の要件は変更しない。同じ提供基盤/履歴/権限/物理ワーカーの共有を開示し、判定不能ならUNKNOWNまたはBLOCKEDを保持する。

## 判定境界
分類そのものに必要な観測が欠落したら`UNKNOWN`（試行済み・証拠不足）または`NOT_TESTED`（未試行）。必須記録が無く後続へ進めないなら`BLOCKED`。宣言と実証が矛盾したら`FAIL`。いずれもGate許可を出さず、中央規約P06の集約規則に従う。

本補訂は文書限定で、実行時分類器・ローカル拡張・AGENTS.md配布・CI強制・既存repoへの適用は**未実装**。検査反例は[合成試験仕様](../tests/actor-classification-cases.md)に分離する。
