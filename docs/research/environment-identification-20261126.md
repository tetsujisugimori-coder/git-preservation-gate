# AI実行環境識別研究 第1次調査報告

- 調査日: 2026-11-26 JST
- 状態: PARTIAL（研究報告・非規範・未独立検証）
- 関連: [Issue #3](https://github.com/tetsujisugimori-coder/git-preservation-gate/issues/3)（実行主体・来歴記録契約）、[PR #4](https://github.com/tetsujisugimori-coder/git-preservation-gate/pull/4)（既存10分類の設計）、Codex-Orchestration-Lab（連携候補）
- 本文は所有者が提示した各セッションの回答・実測報告を整理した公開用二次資料。原コマンド出力・管理応答・全バイトの独立再取得は未実施。公開リポジトリにつき固有ホスト名、ユーザー名、内部パス、個別IDの値は掲載しない。既存規約、実運用許可、保全・独立監査の判定は変更しない。

## 1. 目的と観測方式

通常Chat、Work、Codex、Dotの動作モードと実際の作業先を区別し、回答末尾の環境表示、環境変更の検知、作業継続性、証拠来歴管理に利用できるかを調べた。各セッションに同一の基本質問を行い、ツール使用前の自己認識と実行後の観測を分離した。比較条件の正解ラベルは所有者の利用環境申告であり、独立した製品側の保証とは異なる。

根拠区分:
- SELF_REPORT: AIによる名称・モード・セッション情報の申告。
- REPORTED_MEASUREMENT: 提出された報告上の実測値。本報告作成者による独立観測ではない。
- REPORTED_METADATA: 提出された管理機能・環境属性の応答報告。意味、取得経路、正式サポートの確認は別工程。
- INFERRED: 複数の報告からの推定。
- UNKNOWN: 取得不能・矛盾・不足。NOT_TESTEDは未試験、FAILは既定条件に対する観測済みの不成立として区別する。

## 2. 比較結果

| 所有者申告の環境 | 自己認識 | 報告された作業先・特徴 | 管理情報・判定の限界 |
| --- | --- | --- | --- |
| Web Chat | ChatGPT、GPT-6.2、詳細モード不明 | Linux/Debian 13、root、sh、作業先 / と /mnt/data の存在を報告 | 元の実行原票未確認。ブラウザタブ一覧の観測は現在の入力画面の証明ではない |
| Desktop Chat | ChatGPT、GPT-6、詳細モード不明 | Windows系クライアント情報、CodexBrowser/Chrome識別子 | シェル実測未提出。識別子単独でモードや実行先は確定しない |
| Web Work | Codex、GPT-6系、Work | Debian 13、Linux 6.18.57、x64、agent/UID 1000、Bash、/workspace/scratch配下 | Work Cloudは推定。後述の混合試験とは区別 |
| Desktop Work Local | Codex、GPT-6系、Work | 所有者のWindows 11、ビルド26300.9974、PowerShell 7.6.9、通常ユーザー、Windowsプロジェクト領域 | Work Localは推定。正式ラベル未取得 |
| Work混合 | Codex、Work | 同一スレッドでWindowsからDebian 13.7へ変化 | 後述の照合が報告された。WHは研究上の履歴分類 |
| Codex Desktop Local | Codex、GPT-6系、Desktop、Default | 所有者のWindows、PowerShell 7.6.9、Windowsプロジェクト領域 | projectKind=local、hostId=localと実行先の対応を報告 |
| Codex Cloud | Codex、GPT-6系 | Linux 6.18.57、x64、agent、Bash 5.2.37、/workspace | provider=cloud、starting→running、個別環境IDを報告 |
| Codex CLI Local | Codex、GPT-6系、Default | 所有者のWindows、PowerShell 5.1、別のGit作業領域、書込範囲制限 | CLI自身は起動クライアントを確定できず。Local型と推定 |
| Dot | 個人アシスタントDot、正確なモデル不明 | Debian 13、Linux 6.18.57、x64、Bash 5.2.37、非root | OpenAI管理環境の登録・接続・選択・会話既定先を報告 |

9条件の報告を取得したが、Desktop Chatの実測は未提出。通常ChatのWeb/Desktop/Mobileは画面の区分であり、通常のモデル推論はクラウド利用とする運用上の整理。ただし推論サーバーの物理所在は今回の調査で観測していない。通常Chatのツール実行先や外部連携先も個別に扱う。Work Local/Codex Localは作業実行先を指し、ローカルモデル推論を意味しない。OSやユーザー名だけで分類しない。

## 3. Workの同一スレッドにおける実行先切替

| JST | 条件（所有者申告） | 提出された実測・管理情報 | 個別ターン分類候補 |
| --- | --- | --- | --- |
| 04:22 | DesktopからWork、PC稼働 | Windows、通常ユーザー、PowerShell 7.6.9 | WL（推定） |
| 04:42 | 携帯から同一Workを継続、PC稼働 | Windows、前回とホスト・ユーザー・ビルド・シェル・作業先が一致。CODEX_THREAD_IDとCODEX_SESSION_ID取得 | WL（推定） |
| 04:52 | PC電源OFF後、携帯から継続 | Debian 13.7、Linux 6.18.57、x64、agent/UID 1000、Bash、Linux作業先。管理側の2環境は一方がstarting→ready、他方unavailable。選択環境IDとCODEX_ENVIRONMENT_ID一致 | WC（報告上の管理情報＋実測） |

04:42と04:52で報告されたTHREAD_IDとSESSION_IDはそれぞれ一致。04:22はID未取得で厳密なID照合の対象外。04:42のクライアント識別値 codex_work_desktop と04:52のクライアント付帯情報 CodexBrowser は現在の携帯画面を直接表さない。値の由来・意味は追加確認が必要。

**同一スレッドのLocal・Cloud双方の実行が報告され、今回の試験条件ではWHの成立を支持する。** 今回のターンはWC、履歴分類はWH。WHはOpenAIの正式なモード名ではなく研究上の分類。PC再接続後の復帰は未試験。切替の正確な時刻・操作主体・監査イベント・アカウント全体の登録環境はUNKNOWN。報告時刻は観測の記載時刻であり切替発生時刻とは限らない。

同じ会話で作業先が変わると、OS、ローカルファイル、未pushコミット、インストール済みソフト、権限、作業ディレクトリ、保存先へのアクセスが変わり得る。過去のWorkの不安定さの説明候補となるが、過去案件の原因を一括確定しない。既存の未保存・FAIL・BLOCKEDを解除しない。

## 4. 設計候補（未実装・未採用）

独立した項目として記録する:
- Client: 現在の操作端末、起動元、受信クライアント情報を分離。
- Product/mode: Chat、Work、Codex、Dot。モデル名は別項目。
- Execution: 各コマンド・各ターンのCloud/Local/UNKNOWN。履歴としてHybridを別集計。
- Identity: スレッド、セッション、タスク、環境IDを別フィールドとし、同一値でも同義とみなさない。
- Lifecycle: 管理側の生の状態値と観測時刻、割当・接続・既定・実際の実行を分離。
- Capability/authority: 機能提示、認証、権限、実際の成功を区別。サンドボックス、許可操作、実行主体・委任主体も記録。

現行の接頭辞 CHAT/WC/WL/WH/CC/CL/UNK は維持を候補とし、DOT追加とCodex LocalのDesktop/CLI詳細分類は提案に留める。Issue #3の既存10分類は改変しない。根拠の適用範囲が一致する製品側の情報を優先し、自己認識とコマンド実測で補助する。管理情報との矛盾・欠測はUNKNOWN。単なるLinux/Windows、root/agent、User-Agent、ツールの有無で決めない。

普段の表示では根拠のある推定を明記し、保全・監査では必要な契約に従い独立した原票・実行先・権限・対象の照合を求める。表示上の分類は保全成立・証拠真正性・人的独立性・実行許可を証明しない。

環境変更時の運用候補:
1. 作業開始・継続時に今回の実行先を必要な範囲で確認。
2. 前回の記録と比較し、変更を検出したら通知。
3. 作業継続に必要な固定HEAD、未push/未コミットの有無、必要な原物・ツール・保存先・権限を再確認。
4. 必須条件未達なら影響する作業のみ停止し、許可済みの安全な作業を区別。無断の再取得・代替保存・環境切替・削除は行わない。
5. 作業終了時に実際の実行環境と未確認事項を報告。

## 5. 次工程と受入境界

| 工程 | 内容 | 状態 |
| --- | --- | --- |
| R1 | 9条件の報告収集と比較 | 報告取得済み、独立検証未実施 |
| R2 | Desktop Chat追加実測、Codex CLI起動元、Codex/Dot管理情報の意味・正式サポート、Work環境情報取得経路の確認 | NOT_TESTED |
| R3 | 共通の読取専用プローブ・記録スキーマ・判定規則の設計 | 未実装 |
| R4 | 合成・反復・負対照試験（同一OS異モード、異端末同一実行先、同一スレッド異環境、欠測、矛盾、環境ID再生成、申告偽装、権限不足） | NOT_TESTED |
| R5 | 回答末尾の環境表示に限定した試行導入 | 未承認 |
| R6 | 来歴契約・保全継続条件・オーケストレーションへの適用 | 別レビュー・別承認 |

git-preservation-gateは証拠来歴・保全継続条件を、Codex-Orchestration-Labは割当・状態取得・変更検知・引継ぎの自動化を担当する案。具体的な分担は相手側ロードマップ確認後に確定する。

調査は正規の利用可能な読み取り機能に限定し、認証情報の取得、非公開APIへの無断アクセス、セキュリティ制限回避、環境変数の全件出力、未承認の設定・権限変更を行わない。公開文書は非機密情報のみ。原票の別途保全は対象分類と承認範囲に従う。

## 6. 判定

- 9条件の報告収集: 完了（Desktop Chatの実測は未提出）。
- Work Local継続、PC停止後Cloud切替、同一IDのWH: 提出報告の範囲で成立を支持。
- 独立実証・正式なメタデータ仕様・全環境自動判定: 未確立。
- 総合: PARTIAL。研究文書のみ。production_permit=false。規約変更・実運用開始・既存案件受入・マージの承認ではない。
