# slack-x-bot
# Slack × X (Twitter) 自動スクレイピングBot

このリポジトリは、SlackにX (旧Twitter) のURLが投稿された際に、ツイートの本文・スクリーンショット・エンゲージメント情報を自動で取得し、Slackに整形して再投稿するためのクラウド実行型ツールです。

---

## 📁 ファイル構成

slack-x-bot/
├── main.py # メインロジック（Cloud Functionsで実行）
├── requirements.txt # 依存ライブラリ一覧
├── README.md # プロジェクト説明書
├── .gcloudignore # GCP用ファイル除外設定
└── screenshots/ # （ローカルデバッグ用）スクショ保存先

yaml
コードをコピーする

---

## 📌 主なIssue一覧（機能単位）

### ✅ #1 SlackでXのURLを検知してWebhook送信する
Slackチャンネルで投稿されたメッセージのうち、`https://x.com/` もしくは `https://twitter.com/` を含むものをZapierで検知し、GCP関数にWebhookで送信する。

- Zapierトリガー：Slack新規メッセージ
- Zapierフィルター：URLが含まれるか
- Zapierアクション：Webhook POST
- ペイロード形式：`{ "tweet_url": "https://x.com/123..." }`

---

### ✅ #2 GCPでCloud Functions環境を構築する
Python 3.10環境でCloud Functionsを作成し、GitHubと連携する or ZIPでデプロイできるように設定する。Slack Webhook URL は環境変数で渡す。

- ランタイム：Python 3.10
- トリガー：HTTP
- 認証：未認証呼び出し（テスト目的）
- 環境変数：`SLACK_WEBHOOK=https://hooks.slack.com/...`

---

### ✅ #3 ツイートURLから本文とスクリーンショットを取得する
Playwrightで対象URLを開いて、数秒待ってから全体スクリーンショットを保存する。ツイート本文はHTML要素を抽出して取得する。

- ライブラリ：playwright、requests、bs4（任意）
- スクショ保存：GCP環境では `/tmp/` に一時保存

---

### ✅ #4 Slackに投稿する処理を整える（Webhook形式）
取得した本文・スクショ・リンクをまとめてSlackにWebhook POSTする。

- Slackフォーマット：`text` + `attachments.image_url`
- スクショURLはCloud Storage or Base64対応（後述）

---

### ⏳ #5 エンゲージメント情報（いいね・RT数）を追加する
X APIまたはHTML抽出で `いいね数 / リポスト数 / 閲覧数` などを取得し、Slack投稿に追記する。

- X APIは有料プランのみ→HTML構造での取得が現実的

---

### ⏳ #6 GitHub Actionsで自動デプロイを整備する
コード修正時に自動でGCPにデプロイできるCIを整備する。
testt

---
</details>
