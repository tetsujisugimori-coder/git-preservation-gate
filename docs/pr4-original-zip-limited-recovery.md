# PR #4原証拠ZIP 限定回収記録（2026-11-18 / 未完了）

## 対象と一次優先

- リポジトリ: `tetsujisugimori-coder/git-preservation-gate`、Stage 0補訂 PR #4。
- 元の生成環境: 既報ではWindows / Python 3.14.7、合成反例の作成・再審査時。**元セッションID、原ZIP名、絶対パスは未特定**。
- 固定HEAD: `aaedc1084eed569b70705106e8cc5d10af874cab`、tree: `c7db2532c4c9380ef554499408a1072e4dd26ece`、main: `68285b5a12bf1ef2707543681ba3b3064c2339d4`（本記録作成時の照合対象）。
- 原ZIP報告SHA-256: `6cc0b203291dc3d8481eae91a86da7b0bb90986586adc3fdb9ef23b686c9c15f`、ZIP 89 entries / manifest 88件。**いずれも今回の実測ではない**。サイズ、取得元、現存状態はUNKNOWN。
- 別物として識別: Windows用「保全補助器ZIP」のSHA-256 `d38904b33ec1dde0f56855303c807b5d7d10f645d66ea4cafc3088898e1dbece`。混同・代替禁止。
- 所有者の案件限定承認ID: `GPG-PR4-OWNER-APPROVAL-20261118-01`、保持期限: 2027-11-18 23:59 JST。実際のACL/保持設定の証明にはならない。内部絶対パス・実承認原票は公開しない。

## 限定確認で分かったこと

1. GitHub上の [PR #4](https://github.com/tetsujisugimori-coder/git-preservation-gate/pull/4) と [Review #5953174296](https://github.com/tetsujisugimori-coder/git-preservation-gate/pull/4#pullrequestreview-5953174296) に既知SHA/件数/対象版が記録済み。原ZIP自体、原ファイル名、元セッションの出力先は含まれない。
2. 関連する過去の作業報告・参照可能な会話記録と限定的な添付検索では、元Windows生成時の**絶対パスを確証できなかった**。補助器ZIPリンクを原証拠の回収成功と見なさない。
3. 直近Codex Windows報告では対象作業領域・関連保存履歴を調べて原ZIP未発見。これは不存在の証明ではない。指定の新規保存領域は未作成、実保存/receipt/保存先再取得は未実施。
4. 今回の確認者には元のWindowsファイルシステムへの実行アクセスがなく、現地のフルパス探索・ZIPの実SHA測定は**NOT_TESTED**。既存の元証拠は変更・移動・削除していない。

## 再開手順（原物保護を先行）

1. **対象を限定**: 元Codex CLI作成セッション/その生成ログ、当該repoの既知の作業領域、当時の保存receipt/出力先台帳を読取専用で確認。無関係なドライブ全域・保護領域・他案件へ無承認で探索を拡大しない。再解析ポイント・ACLエラーを区別して記録。
2. **候補ごとに原物照合**: 現物を移動・展開・改変せずサイズとSHA-256を計算。既知SHAと不一致の候補は別物と記録。SHA一致候補だけZIP一覧を安全に読み、89件・manifest 88件・CRC・重複名・危険パス・manifest記載のsize/SHA/contentを確認。圧縮物を無条件に展開・実行しない。
3. **保存前の実効検査**: 非機密区分、承認対象、保存先のACL、容量、保持期限・自動削除条件を確認。UNKNOWNなら転送BLOCKED。
4. **実保存**: 承認済み永続領域の未使用サブフォルダーへ、元ZIPを変えずに新規コピー。上書き禁止。保存先から読み戻してsize/SHA-256/全byteを検査、receiptを非公開に保存。失敗しても原物は残す。
5. **別経路再取得**: 採用済みの規約版に従いB相当の別実行から保存先を直接読んで新しい隔離先へ取得し、byte/SHA/CRC/manifest照合。**v0.1.0のままなら別責任担当者が不在の限りP05はBLOCKED**。単独監査案は[別文書](solo-maintainer-audit-proposal.md)に留まる。
6. **未発見時**: `source_locator=UNKNOWN`、`original_zip=NOT_RECOVERED`、`preservation=BLOCKED` を維持。生成可能なZIPを別版・新規証拠として記録する余地はあるが、旧ZIPと呼ばず、旧監査をPASSに変えない。元セッションが失われたという推測だけで不存在確定にしない。

## 更新要件

担当/セッションID、探索対象を限定した根拠と経路、読取開始/終了、結果、未確認領域、測定したSHA、承認範囲、保存先・receipt・B実測の有無を非公開票に追記。Public PRには検査状態と未解決条件だけ。HEADが変わればレビュー対象版を再固定。原ZIPの回収完了や独立再取得の成功をこの文書だけで主張しない。
