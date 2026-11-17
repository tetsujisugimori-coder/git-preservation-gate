# AI実行来歴レコードの契約（Stage 0補訂、未実装）

[分類定義](actor-execution-taxonomy.md)を、将来のGate A/B/Cから監査できる記録へ落とす設計。既存[architecture](architecture.md)のtarget / custody / verification / independent review各票に`actor_trace_ref`を付けて参照する想定。schema検査器は**まだ存在しない**。

## レコードの必須情報（案）
|field|型・条件|理由|
|---|---|---|
|`schema_version`|固定版の非空文字列|将来改訂との分離|
|`record_id` / `task_id` / `attempt_id` / `execution_id`|各非空で一意|タスク/試行/実行を分離|
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
|`record_digest_ref`|外側の固定receiptへの参照、自己hashを内包しない|事後の差替え・循環参照を避ける|

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

## Gateの受入契約
- **Gate A**: 対象commit/treeと記録の対応、実行主体/環境の取得可能な来歴、固定した規約版を検査する。未pushも同じ対象固定規則。
- **Gate B**: 保存・再取得・隔離復元の各実行について別レコードを残し、担当分離とP03〜P05の原実物取得を確認する。
- **Gate C**: PR HEAD・対象OID・レビュー対象と記録を突合し、規約版/権限・CI判定を個別に確認する。実行主体の分類が合うだけではpermitを出さない。

## 不一致・再試行・委任
同一`execution_id`を別repo/別Git対象/別ワーカーに転用しない。委任先は独自レコードとし、親の処理成功を子の成功と推定しない。リトライ/環境切替時は新attemptを作成し旧失敗票を保持する。分類ラベルと証拠が矛盾した場合はFAIL、必要な情報が未取得ならUNKNOWN/NOT_TESTED、実行または承認が阻害されたならBLOCKEDとして停止。自己申告のactor IDとGitHub認証・OSプロセス本人性の同一視は禁止。

`WORK-LOCAL`はDesktop利用だけで付けない。`WORK-CLOUD-*`は起動面とクラウド実処理が確認できない限り付けない。`DOT`を実行者として記録しても、内部・委任先の処理で別のワーカーが成果物を生成したなら別レコードを必須とする。

## 導入前条件
Stage 1/2でschema版と理由コードを正式採用し、validator・合成正常/故障fixture・独立oraclesを作り、OS別の観測可能性を実測する。分類に必要なUI/ワーカー証拠が取れない製品で全件PASSを強制しない一方、証拠不足をPASSへ読み替えない。既存規約の採用・Stage 1開始・本番運用には別承認が必要。
