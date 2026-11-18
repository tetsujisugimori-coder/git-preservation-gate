# git-preservation-gate

複数AI担当が共有するGit成果物保全ゲート。現在は **Stage 0設計のみ**。実運用ゲート・保全成功・既存案件の復旧を提供した状態ではない。

|段階|対象|現在|
|---|---|---|
|0|中央規約・基本設計・故障試験仕様|本PRで審査する|
|1|bundle、承認済み保存先、再取得、隔離復元、機械検査|NOT_TESTED / 開始承認待ち|
|2|各AI、AGENTS.md、CLI・CIの採用版固定|未実施|
|3|castle-3d-partsで別承認の試験導入、その後横断展開|未実施|

正本は[中央規約v0.1.0](docs/preservation-policy.md)。[構成](docs/architecture.md)、[ゲート契約](docs/gate-contracts.md)、[保存・脅威モデル](docs/security-and-storage.md)、[AI適用計画](docs/ai-integration-plan.md)、[試験台帳](tests/test-plan.md)、[Stage0受入・現状調査](docs/stage0-acceptance.md)を参照。

関連: [Issue #1](https://github.com/tetsujisugimori-coder/git-preservation-gate/issues/1)。main直変更・無承認設定変更・本番適用・マージは本工程に含めない。公開物は設計・仕様のみ。実案件bundleや承認原本をこのPublic repoへ置かない。

## 中央規約 v0.2.0 統合案（未採用）
[Issue #5](https://github.com/tetsujisugimori-coder/git-preservation-gate/issues/5)で、[3段階規約](docs/v0.2.0/policy.md)、[Gate/監査方式](docs/v0.2.0/gates-and-audit.md)、[承認再利用・救済](docs/v0.2.0/authorization-and-rescue.md)、[互換性](docs/v0.2.0/compatibility.md)、[他repo影響](docs/v0.2.0/impact.md)を設計・合成検証する。
正本v0.1.0とPR #4のv0.1.1案は変更しない。v0.2.0の採用、Stage 1開始、他repo適用は別承認。実保全/独立原物監査のPASSを主張しない。

[検証結果](docs/v0.2.0/results.md)と[独立レビュー](docs/v0.2.0/independent-review.md)、[合成試験の実行方法](tests/v0.2.0/README.md)を参照。正式採用・実運用開始は未承認。
