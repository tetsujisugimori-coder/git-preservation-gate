# v0.2.0 合成判定モデル

標準ライブラリのみ。`python -I tests/v0.2.0/run.py --log <新規ログ名>`。全ケースを独立process、5秒上限、retry 0で実行。初期44件の期待値は別担当が実装閲覧前に作成。初回実行後に3件を規範上の理由で訂正し、コードレビュー後にV045〜49を各初回実行前に追加固定した。最終cases.json内expectedは検査器から生成しない。oracle-lock.jsonは入力集合のSHAを固定。初回失敗は保持し、訂正は別票。

実際の原物、ACL、承認、本人性、保存/復元を調べる機能はない。入力status/booleanは合成観測の仮定。gate_eligibilityは仮定上の条件充足であり、permitは常にfalse。実運用には信頼できる観測と対象結合、版採用、操作承認を別途実装/検証する。誤った自己申告から本番許可を出す用途は禁止。

## 入力契約（全field必須、余分field拒否）
- artifact_kind: ordinary/evidence/zip/bundle。level: 整数1/2/3またはUNKNOWN。
- risk: confidential/irrecoverable/destructive/strong_authenticityのboolまたはnull。nullは分類UNKNOWN。trueはLevel3必須。
- mode: SOLO_STANDARD/STRICT_INDEPENDENT。ci_required: bool。
- checks: check.pyのCHECKS全件にPASS/FAIL/PARTIAL/BLOCKED/UNKNOWN/NOT_TESTEDを指定。適用外の値も未実施ならNOT_TESTEDで保持。
- context: session_separated/execution_separated/workspace_separated/direct_storage/independent_input/human_independent/credential_independentをbool/null。資格情報は情報欄であり強制分離は案件追加検査に指定。
- authorization: scope_matches/valid/adopted/individualのbool。保存範囲、有効期間、規約採用、L3個別承認を区別。
- flags: regenerated/retroactive_pass/level_downgrade/claims_third_partyのbool。
- contract_extra_required: 必須追加検査の一意name配列。extra_checks: name→status。必須名欠落はBLOCKED。例 isolation/credential_separation/signature。追加契約を結果確認後に削除しない。

四状態、適用有無、理由、仮定上のGate適合、実permitを完全比較する。FLAGSの不正と既存技術整合は分離するが、再生成物を原物と偽る場合は原物custody/verificationの根拠も失う。分類不正ならL1非適用の特典を認めない。

## SMとの対応
|旧SM|本合成具体化|
|---|---|
|01|V006|
|02|V007|
|03|V002/V025|
|04|V003|
|05|V004/V005/V032|
|06|V012/V013|
|07|V021|
|08|V029|
|09|V008/V011/V028|
|10|V025|

旧SMは未実施の自然文仕様。これはv0.2での具体化実行であって、旧原票の回収/旧実測再現ではない。ATは旧PR固定版を別領域で再実行し旧期待保持。

L1では保存承認scope/期限/individualは非適用、adopted（規約適用）のみ共通。CIやレビュー/公開操作の権限は別契約で省略しない。extra_checksはL1では製品受入C、L2/3では追加内容検証B/Cに適用。L1のB trueは追加archive非適用を含む仮定上の通過で、検証PASSを表さない。

## P2補訂後の再実行
旧 `cases.json` と `oracle-lock.json` は初回49件の原票として不変。旧run.pyは旧期待の比較であり、補訂後はV019/V041の2差分を意図的に報告する（47/49）。旧期待を修正して成功へ合わせない。新規32件は実行前固定。49件の再判定overlayは別ファイルで、V041の見落とし訂正履歴を保存。

repo rootから:
```sh
python tests/v0.2.0/p2/run_fixed.py tests/v0.2.0/check.py tests/v0.2.0/p2/p2-cases.json new32.json
python tests/v0.2.0/p2/run_fixed.py tests/v0.2.0/check.py tests/v0.2.0/p2/legacy49-reassessment-v2.json regression49.json
python tests/v0.2.0/p2/run_fixed.py tests/v0.2.0/check.py tests/v0.2.0/p2/extra-boundary-cases.json extra3.json
```
初回evidence/submission-manifestは初回HEAD専用。本補訂の提出集合は新しいp2/submission-manifestで別に管理。

## 分類違反・独立性の追加境界（I01〜I07）
既存の49件・P2の32件・X01〜03の元入力および元期待は変更しない。別ファイル `p3/independence-boundary-cases.json` に、STRICT人的分離の既知不成立、技術分離の既知不成立、SOLOの同一所有者、人的独立性の未観測の対照を7件固定した。実行例:

```sh
python tests/v0.2.0/p2/run_fixed.py tests/v0.2.0/check.py tests/v0.2.0/p3/independence-boundary-cases.json independence7.json
```

実行時は新規ログ名を使い、`rows=7`・`PASS=7`・`FAIL=UNKNOWN=0` を検証する。ログを取得・照合するまで本追加7件の実行状態は `NOT_TESTED` とする。既存CIも0件なら `NOT_TESTED` のまま維持する。
