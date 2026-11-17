# 保存先・機密保護・脅威モデル

正本は[規約](preservation-policy.md)。Public repoに置けるのは設計/検査仕様/試験仕様/合成非機密fixtureだけ。実案件bundle、非公開ソース、認証情報、実承認原本、内部locatorは公開しない。過去履歴の秘密もbundleへ入るためHEADだけの機密検査は不足。検査が不十分なら公開停止する。

## 保存先契約
保存先候補は所有者管理のWindows永続領域、本人Library、別途承認された保管領域。特定個人のローカルpathやLibrary IDを共通規約へ埋め込まない。案件のprivate custody票に正確なpath/版/権限を記録する。過去の別案件の承認を全環境へ拡張しない。

保存前に対象/データ分類/受領者/権限/目的/保持条件の承認範囲を照合。保存先不達/readonly/容量不足はBLOCKEDで停止。代替先は既承認の同用途範囲でなければ再承認を求める。無断移動/削除/上書きは不可。保存receipt、再取得成功、ACL確認、保持期限確認を別fieldにする。

初版のB PASSには「承認済み永続保管用途の先への保存と実取得」を必須とし、サービスの無期限存続は保証しない。ACL確認が機密分類に対し不足なら転送BLOCKED。長期保持の必要期限を案件ごとに固定し、期限不明または期限不足なら必要契約未達としてBをBLOCKED。一般的な無期限保証はUNKNOWNと記載し、特定期限確認と混同しない。

|脅威/故障|検出/対策|状態と停止|残る限界|
|object欠損、incremental、shallow、外部依存|前提一覧・空bare復元・全object照合|FAIL/契約前提未充足BLOCKED、B/C不可|元消失後は回収不能になり得る|
|bundle破損/転送byte改変|前後size/hash/全byte、復元/fsck|FAIL、受入停止|hashだけで作成者真正性なし|
|manifest/log差替え|固定digest・別担当取得・レビュー対象照合|FAIL、隔離|同一権限者の共謀/全改変は未防御|
|秘密・非公開履歴混入|全到達履歴/追加資産の分類、公開前確認|BLOCKED、送信/公開停止|スキャナーだけで無漏えい証明不可|
|保存/再取得失敗・権限不足|receiptと実取得・期限/容量記録|BLOCKED、完了停止|サービスavailabilityは将来保証なし|
|HEAD差替え/競合|各境界のOID再照合|FAIL、旧対象停止|無排他区間の競合は別防御|
|既存objectによる復元汚染|空DB検査、alternates/env/config排除|FAIL、B/C不可|OS自体の信頼は別審査|
|危険archive path/symlink、悪意あるrepo|展開前一覧・重複/path/mode検査、checkoutしない|FAIL、展開/実行停止|Git parser脆弱性には版管理・隔離が必要|
|環境消失/容量枯渇|Aを早期実行しBを先延ばししない|BLOCKED、残証拠だけ報告|環境破棄そのものの完全阻止不可|
|証拠欠落/担当不在/規約無視|非空schema・独立監査・採用版check|BLOCKED、受入停止|強制層が未導入なら回避可能|

## 証拠の保存期間と公開要約
公開報告は必要なGit OID・検査結果・残件のみ。private locator/認証headerは除去。公開要約から権限ある監査者が原証拠へ辿る対応はprivate台帳に保持。削除/失効後は過去時点PASSと現在再検証可否を別に記録。保持期間延長・ACL変更・削除は独立した承認対象。
