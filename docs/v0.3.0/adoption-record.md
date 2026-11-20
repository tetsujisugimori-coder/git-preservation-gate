# v0.3.0 正式採用記録案

| 項目 | 状態 |
| --- | --- |
| 正式化用Draft PRの作成 | 所有者承認済み。 |
| 正式採用・発効 | 未採用・未発効。正式採用の所有者判断と、正式化PRのレビューは未完了。 |
| 初回適用 | 発効後の中央リポジトリの新規審査・規約解釈。既存案件の移行と他リポジトリへの適用は個別判断。 |
| 発効時点 | 正式採用の記録とレビューを揃えたうえで、正式化PRがmainへマージされた時点。 |
| 現行版 | [v0.2.0](../v0.2.0/policy.md)。 |

採用を決定した場合は、所有者の承認記録、承認日、対象HEADのレビュー、発効条件と適用範囲をここに記録する。規約文書の状態表示とREADMEの現行正本案内を発効条件に合わせて更新し、旧版への参照を残す。

## 審査対象

[規約本文](policy.md)、[Gate・監査契約](gates-and-audit.md)、[承認・原物救済](authorization-and-rescue.md)、[互換・移行手順](compatibility.md)。版番号、初回適用範囲、現行契約と変更する箇所、既知FAILの保持を [Issue #13](https://github.com/tetsujisugimori-coder/git-preservation-gate/issues/13) の方針と照合する。

継承するv0.2.0の参照基準は `793f80e46cda042c8dc7c249419f65dde235e639`。v0.3.0の各文書に指定した範囲で継承し、変更点はv0.3.0側の該当条項を適用する。

## 候補の検証記録

固定HEAD `d4081525f678449d91d1b9c3a9a3f34aab38e6a2` の合成試作で新旧比較16/16、追加境界10/10、現行版回帰156/156、独立追加7/7。既知FAILの保持と、同名衝突の場合に限って別名保存へ進む条件を独立再審査済み。未完ファイルの所在・状態を完成済み保存と区別し、中断時に成功件数が0件となることを合成ケースで確認した。[PR #22の独立再審査](https://github.com/tetsujisugimori-coder/git-preservation-gate/pull/22#pullrequestreview-5991302765) · [P3-01対応確認](https://github.com/tetsujisugimori-coder/git-preservation-gate/pull/22#pullrequestreview-5992308922)

上記はPR #22の固定版の観測結果。正式化PRは規約文書の審査対象であり、候補試作の実行は本番許可を発行しない。実運用環境での保存・再取得は未検証。移行や実運用の受入は [互換・移行手順](compatibility.md) と各案件契約に従う。
