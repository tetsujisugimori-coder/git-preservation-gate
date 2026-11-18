# AI実行来歴レコードの契約（Stage 0補訂、未実装）

[分類定義](actor-execution-taxonomy.md)を、将来のGate A/B/Cから監査できる記録へ落とす設計。既存[architecture](architecture.md)のtarget / custody / verification / independent review各票に`actor_trace_ref`を付けて参照する想定。実運用のschema検査器は**未実装**。[Stage 0合成試験](../tests/actor-classification-cases.md)ではこの契約の一部を試す。

## レコードの必須情報（案）
|field|型・条件|理由|
|---|---|---|
|`schema_version`|固定版の非空文字列|将来改訂との分離|
| `record_id` | 台帳名前空間で一意の非空ID。確定票を追記し、同一IDによる変更・置換を拒否 | 票を固定 |
| `task_id` | 正規化したrepository識別子の名前空間で非空。実行・委任・再試行で同一task_idを共有可能 | 目的を束ねる |
| `attempt_id` | (repository, task_id) 内の非空ID。1試行に複数実行を束ねられる | 試行のまとまりを識別 |
| `execution_id` | 台帳名前空間で一意の非空ID。1イベントに1件の固定票を割り当てる | 実行の再利用を拒否 |
|`actor_kind`|[10分類](actor-execution-taxonomy.md)のいずれか|役割と処理経路の識別|
|`actor_instance_ref`|監査可能な非空仮名ID|分類名と個体識別の分離|
|`client_surface`|web/desktop/mobile/cli/api/automation/other/unknown|起動面とワーカーの分離|
|`execution_site`|cloud/local/hybrid/unknown|実行場所を観測に基づき記録|
|`environment_evidence_refs`|証拠参照配列。観測不能なら理由付き空配列|OS/実行先/権限の裏付け|
|`repository` / `target_commit_oid` / `target_tree_oid`|対象repoと完全OIDを固定。未確定なら未完了|異なるrepo/HEADを混同しない|
|`policy_version` / `policy_commit_oid`|承認規約版と完全OIDを別固定|latestや未承認版への流用を拒否|
|`parent_execution_id`|親イベントIDまたはnull|DOT→Codexなど委任を追跡|
|`handoff_evidence_ref`|親がある場合に必須|委任の言い分だけを証拠にしない|
|`authority_scope_ref`|承認済み権限範囲への参照。なければ不足として記録|書込権限の誤認防止|
|`observation_limitations`|不明範囲の配列（空も可）|同一基盤・権限共用を隠さない|
|`record_digest_ref`|レコード固定前に採番する、digestから独立した外部receiptの非空ID|固定済み原bytesと外部receiptを結ぶ|

日時、コマンド・exit/timeout、実行者の署名/証明、Git/OS版、環境隔離、保存領域・ACL・保持条件は既存Gate票/非公開証拠に記録する。日時だけで順序・真正性を保証しない。実案件の個人情報、機密locator、資格情報をPublic repoへ収録しない。

## 合成記録例（実施証拠ではない）
```json
{
  "schema_version": "actor-trace-draft-0.1",
  "record_id": "example-record-001",
  "task_id": "example-task-001",
  "attempt_id": "example-attempt-001",
  "execution_id": "example-execution-001",
  "actor_kind": "WORK-CLOUD-DESKTOP",
  "actor_instance_ref": "example-actor-A",
  "client_surface": "desktop",
  "execution_site": "cloud",
  "environment_evidence_refs": ["example-observation-001"],
  "repository": "example/repo-a",
  "target_commit_oid": "PLACEHOLDER_NOT_AN_OID",
  "target_tree_oid": "PLACEHOLDER_NOT_AN_OID",
  "policy_version": "0.1.0",
  "policy_commit_oid": "PLACEHOLDER_NOT_AN_OID",
  "parent_execution_id": null,
  "handoff_evidence_ref": null,
  "authority_scope_ref": "example-approval-001",
  "observation_limitations": ["synthetic-fixture"],
  "record_digest_ref": "example-external-receipt"
}
```

OID placeholdersがあるため本例は**故意に未完成**であり、Gateの入力として認めない。実対象では採用版と完全OIDの形式・object存在を別検証する。

## 台帳、再試行、委任
- 台帳を区別して取り込む場合は台帳名前空間も固定し、別台帳のIDを暗黙に結合しない。旧スナップショットの各確定票が新スナップショットにも同一内容で存在することを検査する。スナップショット間で同じ票が再登場することは許容し、同一スナップショット内での重複は拒否する。
- リトライは元試行と同じrepository/task内で新しいattempt_idを採番し、元attemptと原因・結果・入力同一性を参照する。元試行のFAIL票は残す。既に固定した試行の元attemptを後から切り替えない。同じ新試行に実行を追加する場合は元attempt参照を共通にする。
- 委任先は自分のexecution_idを持ち、同じrepository/taskの親execution_idと、その親子を結ぶ非空文字列IDの委任証拠を持つ。親参照は解決でき、自己参照と多段循環がないことを確認する。別repoへの研究上の依頼は別の対象票へ記録し、この親子参照で結合しない。同一OIDの正当な存在は許容し、対象と証拠はrepository、commit/tree、execution単位で結び付ける。
- 受領した証拠の対象組を、固定した対象票の組と照合する。合成試験では固定済みの観測票と旧台帳を外部入力として与える。実運用でこれらを取得・固定し、発行主体を検証する方法は後続工程で扱う。

## 外部receiptの固定順序
1. record_id、execution_idと、内容hashに依存しないreceipt IDを予約する。receipt IDは生成済みのdigestやreceipt実体の内容から導いた参照を値に使わない。
2. record_digest_refに予約済みIDを入れ、レコードをシリアライズして正確なbytesを固定する。
3. 固定済み原bytesのSHA-256を計算する。レコードにdigestを書き戻さない。
4. receiptに予約済みID・対象record_id・SHA-256を入れて固定する。監査ではreceipt ID、対象record_id、固定版原bytesのdigestを照合する。receipt未着はBLOCKED、対象またはdigestの矛盾はFAILとして扱う。

## 単独開発における主体・照合の区別（未採用案）
[単独開発向け監査v0.1.1案](solo-maintainer-audit-proposal.md)は、同じownerによる別セッションBの直接再取得と技術照合を認める一方、別人格・別OS資格情報の独立性が成立したと扱わない。主体、OS account、credential、execution_id、workspace、保存先からの取得経路を個別フィールド/証拠として記録し、共有関係や未知を開示する。採用前は現行v0.1.0 P05による独立担当者不足BLOCKEDを維持する。

## Gateの受入契約
- **Gate A**: 対象commit/treeと記録の対応、実行主体/環境の取得可能な来歴、固定した規約版を検査する。未pushも同じ対象固定規則。
- **Gate B**: 保存・再取得・隔離復元の各実行について別レコードを残し、担当分離とP03〜P05の原実物取得を確認する。
- **Gate C**: PR HEAD・対象OID・レビュー対象と記録を突合し、規約版/権限・CI判定を個別に確認する。実行主体の分類が合うだけではpermitを出さない。

## 不一致・再試行・委任
同一`execution_id`を別repo/別Git対象/別ワーカーに転用しない。委任先は独自レコードとし、親の処理成功を子の成功と推定しない。リトライ/環境切替時は新attemptを作成し旧失敗票を保持する。分類ラベルと証拠が矛盾した場合はFAIL、必要な情報が未取得ならUNKNOWN/NOT_TESTED、実行または承認が阻害されたならBLOCKEDとして停止。自己申告のactor IDとGitHub認証・OSプロセス本人性の同一視は禁止。

`WORK-LOCAL`はDesktop利用だけで付けない。`WORK-CLOUD-*`は起動面とクラウド実処理が確認できない限り付けない。`DOT`を実行者として記録しても、内部・委任先の処理で別のワーカーが成果物を生成したなら別レコードを必須とする。

## 導入前条件
Stage 0の独立期待値と合成fixtureは試験専用とする。Stage 1/2で実運用schema版と理由コードを正式採用し、実入力のvalidatorとOS別の観測可能性を検証する。分類に必要なUI/ワーカー証拠が取れない製品で全件PASSを強制しない一方、証拠不足をPASSへ読み替えない。既存規約の採用・Stage 1開始・本番運用には別承認が必要。
