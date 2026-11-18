# Stage 1-A: synthetic Git bundle roundtrip

既存PR #9を継続する合成用プローブ。実案件repoや原物の入力を受け付けず、新規rootだけに作成する。既存原物は削除・上書きしない。`production_permit=false`。今回の限定受入は、実原物の永続保全や全OSでの安全性の受入ではない。

## 実行
Python 3標準ライブラリとGitが必要。Linuxで検証。必ず未作成の案件専用ディレクトリを指定する。

```sh
python tools/stage1a/synthetic_bundle_gate.py --root /approved/test-parent/new-probe
python tools/stage1a/run_suite.py --root /approved/test-parent/new-suite
```

suiteは固定`cases.json`を読み、期待値を自動更新しない。各Git操作は8秒上限、timeout対照は0.2秒、kill後の直接子waitは2秒。再試行0。stdout/stderr/exit/start/end/process観測を保存する。Linuxでは新process groupへ限定SIGKILLするが、全子孫の独立監査や悪意あるdetachの封じ込めを保証しない。非POSIX環境の動的試験はNOT_TESTED。強い隔離・機密移送・本番permissionは未実装。

## 検査
- 合成3 commit、main/feature、annotated tagを生成。元bundleを保持しコピーだけを故障注入する。
- local config/hook/外部Git環境変数の流入を制限。許可protocolはfileのみ、署名を無効化。OS全体の隔離ではない。
- storage試験領域とretrieved領域を分離し、bundle/manifestを保存先から読戻す。size/SHA/all-byteを原物と照合する。
- SHA-1 v2 bundleのみ。headerを空行終端で検査しprerequisiteを拒否する。
- 未存在の空bareを作成し`git bundle verify`、fetch、fsckを実行。全ref、到達object集合、全保存object集合、各object type/size/内容SHA、commit tree/parentsを照合する。
- shallow/partial/promisor/alternatesとdirty/untracked sourceは合成preflightで拒否する。本番partial cloneを取得・完全化するツールではない。
- 欠落/破損・manifest差替え・Git非ゼロ・timeout・起動不能・記録矛盾を区別する。

## 状態と証拠
`actual.status`は操作結果。`verdict=PASS`は固定期待に一致したという試験判定で、故障入力の保全成功ではない。S24〜S26の外側PASSも四軸保持の契約試験であり、歴史原物を実測した意味ではない。

`CONTENT_INTEGRITY`、`PROVENANCE_STATUS`、`RESTORE_STATUS`、`INDEPENDENCE_STATUS`は独立記録。来歴UNKNOWNは内容PASSを取り消さず、内容PASSは未実施復元をPASSにしない。`axes()`は値の整合記録補助であり、証拠の真正性や所有者承認を認証するものではない。

各runの原ログはroot内に保持。公表票では内部絶対パスをプレースホルダーへ置換し、rawのSHAを併記する。公表票は秘匿部分を除いた派生票でありraw全文の代用とは称さない。fixture/oracle/checker/runner SHA、試行時刻、環境、期待実際、終了コードを追跡する。古い初期probeとその結果は`evidence/stage1a/initial/`に保持する。

## Git bundleの境界
Git bundleは選択したrefsに到達するGit objectを運ぶ。作業treeの未コミット差分・未追跡ファイル、外部Git LFS実体、submoduleの内部repoは、superproject bundleだけでは保存保証できない。LFS pointerやgitlinkのGit objectが一致しても外部実体の復元PASSではない。必要なら別の対象とmanifest・取得/復元工程を定義する。reflog専用の到達不能object、hooks/config、任意のファイル権限、ACL、保持期限、第三者人的独立性も保証しない。

[Git公式bundle仕様](https://git-scm.com/docs/git-bundle)は完全bundleとprerequisite付きbundleを区別する。本試験は後者を不完全な自己完結保全としてBLOCKEDにする設計であり、増分bundle自体が無効形式という主張ではない。

[実施結果・独立レビュー](../../docs/stage1a/results.md) / [来歴例外提案](../../docs/v0.2.0/provenance-exception-proposal.md)
