# 他リポジトリ影響調査（読取限定、2026-11-18 UTC）

## 方法と限界
接続GitHubの `fetch_file` で各repoのdefault-branch `AGENTS.md` を取得し、`fetch_pr_comments` で下記PRのissueコメント・review・inlineを取得した。本文の状態は報告者の主張として読み、原ZIP・実行環境・非公開承認原本を今回再監査したとはしない。取得内容のblob、本文SHA-256、取得経路は [取得index](../../evidence/v0.2.0/impact-source-index.json) に記録。default branchの文書は読み取ったblobに限定し、後日のmainへの不変性を保証しない。

本調査は7 repo・7 PRの限定標本であり、全repo・全AGENTS階層・全作業依頼の網羅調査ではない。Math-Art-LabとLoading-museumのroot AGENTSは当該APIで404。repo内のどこにも規則がないとは判定しない。閲覧した他repo本文に `git-preservation-gate` の文字列参照は見つからなかったが、未取得の履歴・文書・会話からの採用はUNKNOWN。

## 中央規約との因果の境界
[中央v0.1.0 P03/P05/P07](https://github.com/tetsujisugimori-coder/git-preservation-gate/blob/68285b5a12bf1ef2707543681ba3b3064c2339d4/docs/preservation-policy.md)は保存先承認、保存後実物取得、異なるレビュー担当を要求し、独立者不在をBLOCKEDとする。一方、冒頭はStage 0提案版で、規約採用・Stage 1開始・他repo適用に別承認が必要と明記する。P05は同一基盤等の限界を開示し、別Windowsアカウントを全件必須とする文言ではない。[保存契約](https://github.com/tetsujisugimori-coder/git-preservation-gate/blob/68285b5a12bf1ef2707543681ba3b3064c2339d4/docs/security-and-storage.md)は案件別の期限を要求するが、無期限のサービス保証はUNKNOWNでよい。

したがって、中央規約に厳格な契約が存在する事実と、それが各repoの停止を実際に引き起こしたことは別。全案件への採用記録を今回確認しておらず、「共通指示の変更が原因」とは断定しない。

## repo別の観測・分類・v0.2での再審査候補

|repo / 根拠|実際に読めた条件・停止|根拠分類|v0.2設計への示唆・解除しない条件|
|---|---|---|---|
|castle-3d-parts / [AGENTS](https://github.com/tetsujisugimori-coder/castle-3d-parts/blob/main/AGENTS.md)、[PR41 review 5953429397](https://github.com/tetsujisugimori-coder/castle-3d-parts/pull/41#pullrequestreview-5953429397)|AGENTSは別担当確認とDraft/HOLD、研究上の未確認とソフト受入の分離を規定。最新reviewは追加保存の権限不足と元commit未回収を別判定。通常権限、承認済み新規領域、非機密分類、1年間保持を扱う。|repo固有規則＋案件レビュー/依頼に明記。中央由来は未確認。|既承認範囲の保存は重複票を減らせるが、書込権限不足は制度変更で解消しない。元commit未回収・隔離復元未実施は保持。原objectをsource ZIPや再生成物で代替不可。|
|yamanaka-historical-terrain / [AGENTS](https://github.com/tetsujisugimori-coder/yamanaka-historical-terrain/blob/main/AGENTS.md)、[PR55 comment 6974070224](https://github.com/tetsujisugimori-coder/yamanaka-historical-terrain/pull/55#issuecomment-6974070224)|AGENTSに保存後実バイト再取得・独立読戻し・サイズ/hash、適用可能CRC/manifestを明記。Spaceで限定保全が成立すればWindows追加移管や永久保証をマージ前提にしない。B6iにはclose時間上限FAIL、assertions記録不足、ブラウザFAIL、保存先からの再取得未成立。|repo固有規則と実検証失敗。中央因果は未確認。|一般PRを毎回Archiveへ送る規則ではない。重要原票はLevel 2候補。有限process/収録/ブラウザFAILを監査方式変更でPASSにしない。長期保証UNKNOWNを限定保全へ不当に伝播させない。|
|Math-Art-Lab / [固定版archive proposal](https://github.com/tetsujisugimori-coder/Math-Art-Lab/blob/bee889742a769bc0c5ca680dacec2e3d82d6b6cf/docs/three-body/review-44/stage-an/archive-approval.md)、[review 5951486598](https://github.com/tetsujisugimori-coder/Math-Art-Lab/pull/44#pullrequestreview-5951486598)、[review 5953307092](https://github.com/tetsujisugimori-coder/Math-Art-Lab/pull/44#pullrequestreview-5953307092)|先行reviewは別Windows principalを要件として停止。後続reviewは所有者の方針変更を記録し、同一Windowsログインの別セッション/プロセス照合を許容、LIMITED_SAME_ACCOUNTを明記。保持等は残件。|案件限定の文書・レビュー条件と後続所有者方針の報告。中央が別アカウントを強制した根拠なし。AI解釈のみが原因かはUNKNOWN。|SOLO_STANDARDで手続き停止を再審査できる実例。ただし既存3/3退避報告を監査済みに変えずB照合未実施を保持。VM/外部停止機構等は物理安全の別契約で、保全監査の簡素化に巻き込まない。|
|Loading-museum / [PR88 review 5946944597](https://github.com/tetsujisugimori-coder/Loading-museum/pull/88#pullrequestreview-5946944597)、[B-S6報告](https://github.com/tetsujisugimori-coder/Loading-museum/pull/88#issuecomment-6948323239)|原commit/bundle同一性と外部処理無起動を分離。通常Actions抑止見込みと全外部Apps無起動は別。指定原物G0と厳格無起動が未成立ならNO-GO。|案件固有の安全条件・レビュー。中央由来は未確認。|保存方式の簡素化だけでは外部処理UNKNOWNや原物G0を解消できない。原bundle保全を進める文書/読取作業は別に継続可能。|
|intelligence-ui-museum / [AGENTS](https://github.com/tetsujisugimori-coder/intelligence-ui-museum/blob/main/AGENTS.md)、[PR69最終報告](https://github.com/tetsujisugimori-coder/intelligence-ui-museum/pull/69#issuecomment-6947404245)、[文書追補review](https://github.com/tetsujisugimori-coder/intelligence-ui-museum/pull/69#pullrequestreview-5947686489)|AGENTSは旧証拠保持・自己点検/独立レビュー区別、軽微課題を残して進行を許容。原ZIP保全と限定受入の成功が報告され、Windows不可時に既承認Libraryを使用。文書13行追補は既存製品証拠を再使用し、新CIは別途確認。|repo固有方針＋案件での保全実施。過剰BLOCKEDを実証する資料ではない。|Level 1文書更新とLevel 2原票を同一PR内で区別する良例。Stage 3 HOLD・実機/実AI未検証を引継ぎ、全体成功へ拡張しない。|
|historical-source-atlas / [AGENTS](https://github.com/tetsujisugimori-coder/historical-source-atlas/blob/main/AGENTS.md)、[Library承認範囲報告](https://github.com/tetsujisugimori-coder/historical-source-atlas/pull/36#issuecomment-6962683611)、[最新保全報告](https://github.com/tetsujisugimori-coder/historical-source-atlas/pull/36#issuecomment-6974246359)|root AGENTSに毎回Archiveや別アカウントの一律規定なし。原ZIP+監査束のLibrary限定承認とWindows生原票の追加保存は別。実保存2件と長期保持/来歴UNKNOWNを分離。新Archive保存は適用承認未確認として停止。|案件依頼・レビューの承認範囲。中央因果は未確認。|範囲承認を明文化すれば将来の重複確認を減らせる。ただし2件限定承認を全資産に拡張しない。閉鎖専用原票/改稿前byte/来歴UNKNOWNは制度変更で解消しない。|
|calculator-memo / [AGENTS](https://github.com/tetsujisugimori-coder/calculator-memo/blob/main/AGENTS.md)、[verification-policy](https://github.com/tetsujisugimori-coder/calculator-memo/blob/main/docs/agent/verification-policy.md)、[PR147報告](https://github.com/tetsujisugimori-coder/calculator-memo/pull/147#issuecomment-6900102757)、[review 5938666058](https://github.com/tetsujisugimori-coder/calculator-memo/pull/147#pullrequestreview-5938666058)|通常変更は既存CI/LOG/PRを基準。旧ログを現行規則にしない。原ZIP27件の既存Windows保全が報告され、新Library保存なしだけを不合格にしない。HOLDは公開参照/残存リスクと新base整合を含む。|repo固有規則＋機密/公開参照に関する案件条件。中央因果は未確認。|二重保存を一律要求しない実例。公開参照の安全や実データ操作停止はLevel簡素化で解除しない。|

## 5分類での結論
1. 中央規約で実際に要求：v0.1.0の対象内では異なるレビュー担当、保存後実取得、Git自己完結復元、期限付き保存契約が要求される。ただし他repo採用は別承認。
2. repo固有：山中城の保全条項、castleの別担当確認、Calculatorの通常CI基準を実取得した。
3. 作業依頼/案件条件：Mathの保存承認原票・別principal、Loadingの厳格無起動、Atlasの限定承認はPR記録に明記される。公開レビューが所有者発言を報告している場合、原承認を直接検証したとはしない。
4. AIの厳格解釈：その可能性はあるが、担当AIの判断過程と当時適用指示を全件再構成しておらず、単独原因と確定した例は0件。Mathの別principal条件が中央より強いことは観測できる。
5. 原因未確認：共通指示変更から全repoへ伝播した因果、未取得の階層AGENTSや別会話の追加条件。UNKNOWNを維持する。

## 再分類の提案（採用・適用ではない）
承認票重複・別人不在だけの停止は、範囲承認とSOLO_STANDARD適合を確認した後に追記型再審査の候補とする。原物未回収、byte不一致、期限/受取権限未成立、保存先不達、秘密混入、Git復元未証明、正式検証FAILは従来停止を維持する。既存PRの判定変更、設定変更、保存、実験、マージは本調査では0件。
