# AI担当への適用計画（Stage2、未実施）

八兵衛、Codex CLI、Codexクラウド、その他AIは同じ[規約](preservation-policy.md)を参照する。役割名だけでidentityや独立性が成立したと扱わない。

## 採用マニフェスト案
各repoのAGENTS.mdと作業依頼へ `policy_version: 0.1.0`、承認された中央完全commit SHA、文書path/hash、検査器版/hash、採用範囲、案件のGate契約、owner承認参照を記載する。Stage0では採用先用の実SHAは未確定でOPEN。`main/latest`参照だけは禁止。未設定・参照不能はBLOCKED、過去cacheを確認済み最新版とはしない。

## 周知と実効性
1. ownerが案件別採用範囲と保存先を承認する。
2. AI開始時に版と権限を読み、A/B/Cを作業計画・完了チェックへ組み込む。
3. CLI wrapper/hookはローカルの早期検出、CIは提出版の確認を担う。
4. required checkとbranch保護を別提案・別承認で設定し、bypass含む故障試験で検証する。
5. reviewerは実証拠を取得し、自己申告や緑色checkだけで受入れない。

導入していないclient、管理者、直接API、設定変更には回避余地がある。周知だけで完全強制・独立レビュー必須とは言わない。Stage0ではAGENTS追加や他repo設定は実施しない。

## 更新統治
規約/検査器/schemaの変更は専用Issue→branch→互換性表→合成故障試験→別担当レビュー→owner採用判断。中央mergeと各repoの採用更新は別。既存採用版は自動更新しない。破壊的変更には移行計画・旧証拠再評価の必要範囲を記す。回帰時は新規採用を停止し、証拠保持したまま承認済み旧版へ戻す提案を行う。失敗をPASSへ再採点しない。

城郭3DはStage3の最初の候補だが未導入。元commit回収BLOCKEDは背景例であり、本工程は復旧・再生成・代替採用をしない。
