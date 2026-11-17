# 構成と信頼境界

Stage0は[中央規約](preservation-policy.md)を実装可能にする設計。実装、connector、署名鍵、CI強制設定はまだない。

```text
固定対象repo → 生成担当/検査器 → 承認済み保存アダプター → 保管サービス
       │             │                                  │
       └─固定対象票───┴─来歴/結果                         └→ 独立取得者
                                                               │
                                                    新規空bare / 全object検証
                                                               │
                                                    監査結果 → 受入判定者
```

## 境界と責任
- 実装担当: 中央検査器・schemaの実装と自己試験。自身の出力を独立認定しない。
- 保存担当: 固定対象、bundle生成、承認された転送と再取得。生成と保存は同一者可、監査とは分離。
- 独立監査担当: 保存版を直接取得・隔離復元し対象を照合。別担当でも共通基盤の限界を明記。
- 所有者/受入責任者: 保存先/公開/例外/採用版/マージの承認。検査不一致を承認だけでPASSに変更しない。
- 外部保存先: availability/ACL/保持保証を個別に観測。receiptの成功を永続性保証にしない。

## データモデル（仕様、未実装）
1. target record: schema版、規約version＋規約commit、案件ID、repo、object_format、target_commit、tree、ordered_parents、refs一覧、到達object集合digest、非Git資産/除外、生成主体・環境。
2. bundle manifest: 相対名、size、SHA256、bundle format、prerequisites=[]、対象ID、生成コマンド/版/exit、必要object一覧とそのdigest。
3. custody record: 承認記録参照、保存先の非公開locator、保存版、保存/再取得時刻、各size/hash、全byte比較、取得担当、制約。
4. verification record: attempt ID、入力digest、ゲート別検査ID、状態・理由・証拠参照、開始終了・exit/timeout、復元先が空であった証拠、fsck結果、object照合。
5. independent review: 別担当identity、共有要素、取得/復元結果、レビュー対象digest、指摘/閉鎖原票。
6. acceptance record: 上記immutable digest参照、各必須状態、permit bool、所有者判断。自身のdigestを自身に含めず、別receiptから固定する。

証拠は追記専用版で関係付ける。公開要約と非公開原票を分ける。署名者認証・時刻真正性・不変ストレージはOPEN、自己申告だけでは真正性を保証しない。manifestとpayloadを同じ攻撃者が変更できる場合にhash一致は防御にならない。

## Git整合の根拠と設計判断
Git公式[git-bundle](https://git-scm.com/docs/git-bundle)はprerequisite付きbundleを許す。verifyは受信repoに依存する検査でもあり、単独の空環境復元の証明ではない。このため初版はprerequisiteなしに限定する（本プロジェクトの選択）。
[git-fsck](https://git-scm.com/docs/git-fsck)はobjectの整合性・接続性を検査する。検査対象と設定を固定し、connectivity-onlyを全blob検査の代用にしない。
[format](https://git-scm.com/docs/gitformat-bundle)にはprerequisite/ref/packがある。branch名とその指すOIDは別々に固定する。これらは2026-11-17に文書確認した根拠であり動作試験結果ではない。Stage1では利用Git版を固定し仕様対応を試験する。

## 更新の波及抑止
検査器と規約は版固定、各案件opt-in。中央更新は自動配布しない。canaryは合成repoのみ、互換表と独立故障試験後に個別承認で移行。旧証拠は旧schemaで保持し新規約の成功へ読み替えない。
