# v0.3.0 正式採用記録

| 項目 | 状態 |
| --- | --- |
| 所有者の正式採用承認 | **2026-11-24 JST、v0.3.0の正式採用を明示承認**。対象は [PR #25](https://github.com/tetsujisugimori-coder/git-preservation-gate/pull/25)。規約文書の限定技術受入とマージ判断を承認し、実運用の許可は含めない。 |
| 独立レビューの根拠 | PR #25の固定HEAD `936747d1a33c5a95d959f211335160b9462df56b` の [独立再審査](https://github.com/tetsujisugimori-coder/git-preservation-gate/pull/25#pullrequestreview-6011845041) と [正式CI](https://github.com/tetsujisugimori-coder/git-preservation-gate/actions/runs/45014278969)。P2/P3計4件CLOSED、文書・局所検査限定PASS。採用表示修正後の最終HEADは別途マージ直前に照合する。 |
| 発効条件・時点 | **PR #25の最終HEAD・必要CI・変更差分を確認したうえでmainへマージした時点**で発効。マージ前はv0.2.0が有効。発効日時とマージコミットの一次記録はPR #25のGitHubマージ記録とする。 |
| 初回適用範囲 | **発効後の中央リポジトリの新規審査・規約解釈**。既存案件の自動移行、他リポジトリへの一律適用、過去のFAIL/BLOCKED/HOLD解除は行わず、案件単位で判断する。 |
| 実運用の許可 | **今回発行しない（`production_permit=false`）**。実データ取得・保存・再取得等は対象別の実運用必須6条件を別途満たす必要がある。 |
| 旧版と適用版 | マージ前は [v0.2.0](../v0.2.0/policy.md)、マージ後の初回適用範囲では [v0.3.0](policy.md)。旧版の証拠と既存案件の適用契約を保持する。 |

所有者の採用承認、適用範囲、発効条件は上表に記録した。規約の状態表示とREADMEの現行正本案内は、mainへのマージ前後を区別して表示し、旧版への参照を残す。実運用の許可は別判断とする。

状態表示やREADMEを更新した後の最終HEADを固定し、審査済みHEADとの差分を確認する。既存の審査結果は前提が同じ範囲で再利用し、採用・発効・適用範囲の判断に影響する差分は独立再審査する。マージ直前に対象HEADと必要な確認結果がその最終版に対応していることを確認する。

## 審査対象

[規約本文](policy.md)、[Gate・監査契約](gates-and-audit.md)、[承認・原物救済](authorization-and-rescue.md)、[互換・移行手順](compatibility.md)。版番号、初回適用範囲、現行契約と変更する箇所、既知FAILの保持を [Issue #13](https://github.com/tetsujisugimori-coder/git-preservation-gate/issues/13) の方針と照合する。

継承するv0.2.0の参照基準は `793f80e46cda042c8dc7c249419f65dde235e639`。v0.3.0の各文書に指定した範囲で継承し、変更点はv0.3.0側の該当条項を適用する。

## 候補の検証記録

固定HEAD `d4081525f678449d91d1b9c3a9a3f34aab38e6a2` の合成試作で新旧比較16/16、追加境界10/10、現行版回帰156/156、独立追加7/7。既知FAILの保持と、同名衝突の場合に限って別名保存へ進む条件を独立再審査済み。未完ファイルの所在・状態を完成済み保存と区別し、中断時に成功件数が0件となることを合成ケースで確認した。[PR #22の独立再審査](https://github.com/tetsujisugimori-coder/git-preservation-gate/pull/22#pullrequestreview-5991302765) · [P3-01対応確認](https://github.com/tetsujisugimori-coder/git-preservation-gate/pull/22#pullrequestreview-5992308922)

上記はPR #22の固定版の観測結果。正式化PRは規約文書の審査対象であり、候補試作の実行は本番許可を発行しない。実運用環境での保存・再取得は未検証。移行や実運用の受入は [互換・移行手順](compatibility.md) と各案件契約に従う。
