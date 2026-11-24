# git-preservation-gate

**Issue #14 最新判定（2026-11-19 JST）**　総合 **PARTIAL**。Level 1の簡素化と明示保存の分離は合成自己検証済み。固定版の独立レビュー待ちのため限定技術受入・限定マージ推奨は **NO**。`production_permit=false`。固定版、正式CI、回帰結果は [Draft PR #19](https://github.com/tetsujisugimori-coder/git-preservation-gate/pull/19) と [Issue #14 入力仕様](docs/stage1b/issue14-level1-defaults.md) を参照。

複数AI担当・複数リポジトリで共通利用するGit成果物の保全・検証・監査規約と、その実装を開発するプロジェクト。

**中央規約の現行正本は、[PR #25](https://github.com/tetsujisugimori-coder/git-preservation-gate/pull/25)のmainマージ前は [v0.2.0](docs/v0.2.0/policy.md)、マージ後は [v0.3.0](docs/v0.3.0/policy.md) です。** v0.3.0の所有者正式採用承認日は2026-11-24 JST、発効はPR #25のmainマージ時です。初回適用は発効後の中央リポジトリの新規審査・規約解釈に限定し、既存案件と他リポジトリの移行は別判断です。[v0.3.0採用記録](docs/v0.3.0/adoption-record.md) / [v0.2.0採用記録](docs/v0.2.0/adoption-record.md)を参照。旧版と旧判定は履歴として保持します。

| 段階 | 対象 | 現在 |
| --- | --- | --- |
| Stage 0 | 中央規約、監査方式、故障系の設計・合成 | **v0.3.0所有者採用承認済み（PR #25のmainマージ時に発効）**。文書・合成限定受入であり実保全PASSではない |
| Stage 1 | Git bundleの作成・保存・再取得・隔離復元・有限停止 | **開発・試験中**。Stage 1-AのLinux合成プローブは限定受入済み、本番実保存・全OS・強制ゲートは未受入 |
| Stage 2 | AI/AGENTS.md/Codex CLI/CIへの版付き連携 | 計画・個別評価の対象。自動強制は未導入 |
| Stage 3 | castle-3d-partsを起点とする横断パイロット | 段階的展開方針を承認済み。各repoの導入・マージは別審査 |

## v0.3.0の判断基準（発効前の案件はv0.2.0を適用）

- **Level 1**：通常の公開コード・文書はGit履歴、案件別CI・レビューを基本とし、Archive、別アカウント、ZIP等を一律に必須としない。
- **Level 2**：重要原物は承認済み永続先への実保存と保存先からの直接再取得、size/SHA-256・必要な全byte/ZIP/manifest検査を維持する。同一所有者の別セッション技術監査は条件付きで可能だが第三者人的独立性PASSとはしない。
- **Level 3**：所有者指定または規約上の最低Level 3が確定した機密保護対象。個別承認、実効ACL、事前固定した追加安全契約を要求する。非機密の喪失・破壊リスクはLevel 2でも個別保護する。別アカウントやVMは案件リスクに応じる。

[v0.3.0 Gate/監査契約](docs/v0.3.0/gates-and-audit.md) / [承認再利用・原物救済](docs/v0.3.0/authorization-and-rescue.md) / [互換・移行手順](docs/v0.3.0/compatibility.md)。v0.2.0の[合成結果](docs/v0.2.0/results.md)と[独立設計レビュー](docs/v0.2.0/independent-review.md)も引き継ぎ範囲の根拠として保持する。

## 適用と制限

**規約の正式採用 ≠ Stage 1の本番実装・検証完了 ≠ 個々の保存操作の承認 ≠ PR受入・マージ許可。** Stage 1の合成プローブは `production_permit=false`、正式CIやWindows実測、実保存先の権限・保持、実原物の監査を自動的にPASSとしない。

他repoには**段階的に適用**し、そのrepoのIssue/branch/PRで対象、採用版、既存契約、既存承認範囲と証拠を個別に確認する。既存のFAIL/BLOCKED/HOLDを一括解除しない。実証済み破損・不一致、安全条件の未達は維持し、旧判定は追記型の新attemptで再審査する。

**既存承認の再利用**は、対象・分類・保存先・主体・操作・ACL・保持期間・削除条件・承認の有効期間が一致するときに限る。中央規約の採用は、他repoで言及された**PR #23の個別の保存操作を無条件承認するものではない**。

公開GitHubには実案件原物、非公開承認票、内部の保存先locatorや機密情報を掲載しない。mainへの直接変更は禁止し、規約改訂もbranch/PR/レビューで管理する。

## 横断運用の実例

[Codex-Orchestration-Lab PR #23：原物保全・文書受入・マージ判断の分離](docs/operations/pr23-preservation-and-pr-acceptance-20261119.md)（2026-11-19、v0.2.0の適用例）。Level 1の通常Git管理とLevel 2重要原物の保全を別判定し、承認の再利用、別セッション監査、所有者受入、マージ実行権限を混同しないための**非規範の運用補助資料**です。規約変更・本番許可・各案件のHOLD解除ではありません。

## Stage 1-B

[実保存契約・Windows有限停止・限定パイロット（開発中）](docs/stage1b/README.md)。合成/P0技術確認と実保存許可を分離し、production_permit=falseを維持します。

## Stage 1-B2 limited save pilot

See [scope and gated results](docs/stage1b2/README.md). This does not enable production preservation or supersede Issue14.

## Issue #14 Level 1 standard-input simplification (Draft)

[Issue #14](https://github.com/tetsujisugimori-coder/git-preservation-gate/issues/14) is a separate follow-up: ordinary Git documents use default inputs without extra archive approval, destination, retention or audit fields. See [compact input and separated explicit-save evaluation](docs/stage1b/issue14-level1-defaults.md). This is synthetic-only, does not alter Level 2/3 or authorize real saves or production.
