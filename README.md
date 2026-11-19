# git-preservation-gate

**Issue #14 最新判定（2026-11-19 JST）**　総合 **PARTIAL**。Level 1の簡素化と明示保存の分離は合成自己検証済み。固定版の独立レビュー待ちのため限定技術受入・限定マージ推奨は **NO**。`production_permit=false`。固定版、正式CI、回帰結果は [Draft PR #19](https://github.com/tetsujisugimori-coder/git-preservation-gate/pull/19) と [Issue #14 入力仕様](docs/stage1b/issue14-level1-defaults.md) を参照。

複数AI担当・複数リポジトリで共通利用するGit成果物の保全・検証・監査規約と、その実装を開発するプロジェクト。

**中央規約の現行正本は [v0.2.0](docs/v0.2.0/policy.md)（2026-11-18 JST 正式承認・発効）です。** [採用記録と版差分](docs/v0.2.0/adoption-record.md) / [承認を記録したIssue #5](https://github.com/tetsujisugimori-coder/git-preservation-gate/issues/5) を参照。従来の [v0.1.0](docs/preservation-policy.md) とPR #4のv0.1.1案は歴史的参照として保持し、v0.2.0の採用で旧判定を書き換えません。

| 段階 | 対象 | 現在 |
| --- | --- | --- |
| Stage 0 | 中央規約、監査方式、故障系の設計・合成 | **v0.2.0規約正式採用**。設計・合成限定受入であり実保全PASSではない |
| Stage 1 | Git bundleの作成・保存・再取得・隔離復元・有限停止 | **開発・試験中**。Stage 1-AのLinux合成プローブは限定受入済み、本番実保存・全OS・強制ゲートは未受入 |
| Stage 2 | AI/AGENTS.md/Codex CLI/CIへの版付き連携 | 計画・個別評価の対象。自動強制は未導入 |
| Stage 3 | castle-3d-partsを起点とする横断パイロット | 段階的展開方針を承認済み。各repoの導入・マージは別審査 |

## v0.2.0の判断基準

- **Level 1**：通常の公開コード・文書はGit履歴、案件別CI・レビューを基本とし、Archive、別アカウント、ZIP等を一律に必須としない。
- **Level 2**：重要原物は承認済み永続先への実保存と保存先からの直接再取得、size/SHA-256・必要な全byte/ZIP/manifest検査を維持する。同一所有者の別セッション技術監査は条件付きで可能だが第三者人的独立性PASSとはしない。
- **Level 3**：機密・破壊リスクなどに応じ個別承認、実効ACL、事前固定した追加安全契約を要求する。別アカウントやVMは一律義務でなく案件リスクに応じる。

[Gate/監査契約](docs/v0.2.0/gates-and-audit.md) / [承認再利用・原物救済](docs/v0.2.0/authorization-and-rescue.md) / [v0.1.0との差分](docs/v0.2.0/compatibility.md) / [合成結果](docs/v0.2.0/results.md) / [独立設計レビュー](docs/v0.2.0/independent-review.md)。

## 適用と制限

**規約の正式採用 ≠ Stage 1の本番実装・検証完了 ≠ 個々の保存操作の承認 ≠ PR受入・マージ許可。** Stage 1の合成プローブは `production_permit=false`、正式CIやWindows実測、実保存先の権限・保持、実原物の監査を自動的にPASSとしない。

他repoには**段階的に適用**し、そのrepoのIssue/branch/PRで対象、採用版、既存契約、既存承認範囲と証拠を個別に確認する。既存のFAIL/BLOCKED/HOLDを一括解除しない。実証済み破損・不一致、安全条件の未達は維持し、旧判定は追記型の新attemptで再審査する。

**既存承認の再利用**は、対象・分類・保存先・主体・操作・ACL・保持期間・削除条件・承認の有効期間が一致するときに限る。中央規約の採用は、他repoで言及された**PR #23の個別の保存操作を無条件承認するものではない**。

公開GitHubには実案件原物、非公開承認票、内部の保存先locatorや機密情報を掲載しない。mainへの直接変更は禁止し、規約改訂もbranch/PR/レビューで管理する。

## Stage 1-B

[実保存契約・Windows有限停止・限定パイロット（開発中）](docs/stage1b/README.md)。合成/P0技術確認と実保存許可を分離し、production_permit=falseを維持します。

## Stage 1-B2 limited save pilot

See [scope and gated results](docs/stage1b2/README.md). This does not enable production preservation or supersede Issue14.

## Issue #14 Level 1 standard-input simplification (Draft)

[Issue #14](https://github.com/tetsujisugimori-coder/git-preservation-gate/issues/14) is a separate follow-up: ordinary Git documents use default inputs without extra archive approval, destination, retention or audit fields. See [compact input and separated explicit-save evaluation](docs/stage1b/issue14-level1-defaults.md). This is synthetic-only, does not alter Level 2/3 or authorize real saves or production.
