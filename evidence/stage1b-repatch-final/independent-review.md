# Stage 1-B P2-B01/B02 独立技術再審査B（公開固定版）

対象は `1014154c6db51d250352b5038a0add215ef13c38`、tree `aa6403d4375a043d630134cea769db0eb3266a05`。GitHub HTTPSから別領域へ新規clone後、公開commitをfetchして実行した。実装AのPASSを採点根拠にはしない。別AI実行コンテキスト・別領域・取得操作・判定を分離したが、同一所有者・基盤・filesystem・継承履歴を共有するため `LIMITED_SHARED_OWNER`。第三者人的独立監査ではない。

## 実行事実
Linux / Python 3.12.14 / Git 2.52.0。各wrapper上限240秒、契約内コマンド20秒、再試行0。stdout/stderr、開始終了時刻、exit code、使用ソースSHAを新原票へ記録した。

- 既存契約50、既存独立反例10、新規P2反例18、Stage 1-A32：計110件期待一致。
- 固定レビュー12＋NEW13：13/13。
- 追加補訂境界：17/17。
- 公開記録scanner：10/10。
- B固定追加oracle：78/78。64のactive/covered risk組合せ、L1/L2分離8、STRICT3、CI/review2、分類違反＋既知SHA FAIL1。oracle SHA-256 `49748b38f586809d1525e8626c3927c2f852f1e0d3cb58a1fa23aeeec343e2c9`。
- 全コマンドexit 0。故障入力は期待どおり拒否したという意味であり、故障対象自体の受入PASSではない。production_permit=false。
- Windows21は本BのLinux実行で代用しない。別Windows担当の固定版結果を別に評価する。

## 指摘判定
P2-B01：補訂確認。L1 Git文書はarchive_applicability.required=falseと理由を明記し、非適用3軸はNOT_TESTED。非適用の分離不足が受入BLOCKEDへ伝播しない。HEAD・CI・review不成立、分類違反とL2/3停止は維持。

P2-B02：補訂確認。対象外riskはSCHEMA_INVALID＋RISK_NOT_APPLICABLE、未知名・重複は別理由で拒否。必要risk欠落はEXTRA_CONTRACT_UNKNOWNとして停止。将来仕様を導入していない。

P3-B03：補訂確認。STRICTかつ既知shared_owner=trueはBLOCKED。SOLO_STANDARDの限定性は別記録。人的独立性の証明はしない。

P2-03：既存CLOSEDを維持。CI非適用のscope/理由/矛盾と必須FAIL保持を確認。

旧50件のC26/C27は意図的な仕様補訂。旧期待・旧overlayを保持し、新overlayで説明している。旧期待48/50を消していない。元固定oracle5種は旧公開c52194dcと全byte一致。

## 提出物監査
GitHubのPR全ページ変更一覧は172 path。base4695c3ceからのGit差分集合と一致。公開commitから取得した全172ファイルを、実装原稿との全byte・size・SHA-256およびGit blob OID再計算で照合し一致した。旧local8d6cと公開1014154はcommit OIDが異なるがtreeは一致。新manifest60件・旧manifest77件は集合、重複なし、size/SHA一致。

B自身の初回集合監査で、旧manifest配下の管理ファイルまで除外する検査側の誤りがあった。初回原票を保持し、除外を対象manifest自身だけに訂正した再検算で全77件一致。提出物は変更していない。

## 限界と暫定判定
新規未解決P1/P2なし。歴史的未参照blobのpath公開P3 OPENと旧cloud未公開生原票保持UNKNOWNは維持。scannerは対象固定反例の拒否であり、全秘密検出保証ではない。

技術照合VERIFICATION=PASS（公開固定版Linux合成・提出物の限定範囲）。実原物の恒久保存CUSTODYは本審査NOT_TESTED、INDEPENDENCEはLIMITED_SHARED_OWNER、実運用ACCEPTANCEは未承認。正式CI・Windowsと最終文書版の照合を別途完了してから、限定技術受入・限定マージ推奨を確定する。実保存adapter、実効ACL・保持保証、実容量不足・lock、controller完全停止、外部承認認証、本番移行は対象外のまま。

本書時点は総合PARTIAL。B01/B02/B03は技術上閉鎖可能。P3-B04は最終PR本文・結果文書への現行判定反映確認待ち。

## 別担当から受領した追加証拠（本Bの再実行とは別）
Windows担当は公開1014154を新規取得しPowerShell 5.1/7で各21件、exit 0と報告。親が確認した正式push CI 44398709869は2 jobs/checks成功。最終文書commit読戻し後に採否を確定する。
