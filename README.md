# git-preservation-gate

複数AI担当が共有するGit成果物保全ゲート。現在は **Stage 0設計のみ**。実運用ゲート・保全成功・既存案件の復旧を提供した状態ではない。

|段階|対象|現在|
|---|---|---|
|0|中央規約・基本設計・故障試験仕様|PR #2文書限定マージ済み。技術実測は未実施|
|1|bundle、承認済み保存先、再取得、隔離復元、機械検査|NOT_TESTED / 開始承認待ち|
|2|各AI、AGENTS.md、CLI・CIの採用版固定|未実施|
|3|castle-3d-partsで別承認の試験導入、その後横断展開|未実施|

正本は[中央規約v0.1.0](docs/preservation-policy.md)。[構成](docs/architecture.md)、[ゲート契約](docs/gate-contracts.md)、[保存・脅威モデル](docs/security-and-storage.md)、[AI適用計画](docs/ai-integration-plan.md)、[AI実行主体10分類](docs/actor-execution-taxonomy.md)、[実行来歴契約](docs/execution-provenance-contract.md)、[試験台帳](tests/test-plan.md)、[AI分類の合成反例12件](tests/actor-classification-cases.md)、[Stage0受入・現状調査](docs/stage0-acceptance.md)を参照。

関連: [Issue #1](https://github.com/tetsujisugimori-coder/git-preservation-gate/issues/1)・[Stage 0補訂Issue #3](https://github.com/tetsujisugimori-coder/git-preservation-gate/issues/3)。main直変更・無承認設定変更・本番適用は行わない。Stage 0補訂のDraft PRは別審査までマージしない。公開物は設計・仕様のみ。実案件bundleや承認原本をこのPublic repoへ置かない。
