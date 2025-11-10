import os
import json
import functions_framework
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import requests


def get_tweet_content_and_screenshot(tweet_url: str, screenshot_path: str = "/tmp/tweet.png"):
    """
    ツイートURLから本文とスクリーンショットを取得する
    
    Args:
        tweet_url: ツイートのURL
        screenshot_path: スクリーンショットの保存先パス
        
    Returns:
        dict: {'text': ツイート本文, 'screenshot_path': スクリーンショットのパス}
    """
    with sync_playwright() as p:
        # Chromiumブラウザを起動（headlessモード）
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        try:
            page = browser.new_page(
                viewport={'width': 1280, 'height': 1024}
            )
            
            # ツイートページにアクセス
            page.goto(tweet_url, wait_until='networkidle', timeout=30000)
            
            # ページが完全に読み込まれるまで少し待機
            page.wait_for_timeout(2000)
            
            # スクリーンショットを取得
            page.screenshot(path=screenshot_path, full_page=True)
            
            # HTMLを取得
            html_content = page.content()
            
            # BeautifulSoupでHTMLを解析
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # ツイート本文を抽出（複数の方法を試す）
            tweet_text = ""
            
            # 方法1: data-testid="tweetText"を探す
            tweet_element = soup.find('div', {'data-testid': 'tweetText'})
            if tweet_element:
                tweet_text = tweet_element.get_text(strip=True)
            
            # 方法2: article内のテキストを探す（フォールバック）
            if not tweet_text:
                article = soup.find('article')
                if article:
                    # lang属性を持つdivを探す（ツイート本文の可能性が高い）
                    text_divs = article.find_all('div', {'lang': True})
                    if text_divs:
                        tweet_text = ' '.join([div.get_text(strip=True) for div in text_divs])
            
            # 方法3: 最終手段としてarticle全体からテキストを抽出
            if not tweet_text:
                article = soup.find('article')
                if article:
                    tweet_text = article.get_text(separator=' ', strip=True)[:500]  # 最初の500文字
            
            return {
                'text': tweet_text if tweet_text else "ツイート本文を取得できませんでした",
                'screenshot_path': screenshot_path
            }
            
        finally:
            browser.close()


def post_to_slack(webhook_url: str, text: str, image_path: str = None):
    """
    Slack Webhookに投稿する（後のIssueで実装予定）
    
    Args:
        webhook_url: Slack Webhook URL
        text: 投稿するテキスト
        image_path: 画像ファイルのパス（オプション）
    """
    # TODO: Issue対応時に実装
    # 画像をアップロードする場合は、Slack APIのfiles.uploadを使用する必要があります
    payload = {
        "text": text,
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text
                }
            }
        ]
    }
    
    response = requests.post(webhook_url, json=payload)
    return response.status_code == 200


@functions_framework.http
def main(request):
    """
    Cloud Functions エントリーポイント
    
    リクエストパラメータ:
        - tweet_url: ツイートのURL（必須）
        - slack_webhook_url: Slack Webhook URL（オプション）
    """
    try:
        # リクエストからパラメータを取得
        request_json = request.get_json(silent=True)
        request_args = request.args
                # ✅ Slack Event APIの challenge 検証
        if request_json and 'challenge' in request_json:
            return json.dumps({'challenge': request_json['challenge']}), 200

        
        if request_json and 'tweet_url' in request_json:
            tweet_url = request_json['tweet_url']
            slack_webhook_url = request_json.get('slack_webhook_url')
        elif request_args and 'tweet_url' in request_args:
            tweet_url = request_args['tweet_url']
            slack_webhook_url = request_args.get('slack_webhook_url')
        else:
            return json.dumps({
                'error': 'tweet_url パラメータが必要です'
            }, ensure_ascii=False), 400
        
        # ツイートの内容とスクリーンショットを取得
        result = get_tweet_content_and_screenshot(tweet_url)
        
        # Slack通知（Webhook URLが指定されている場合）
        if slack_webhook_url:
            post_to_slack(
                webhook_url=slack_webhook_url,
                text=f"ツイート本文:\n{result['text']}\n\nURL: {tweet_url}"
            )
        
        # レスポンスを返す
        return json.dumps({
            'success': True,
            'tweet_text': result['text'],
            'screenshot_saved': result['screenshot_path'],
            'tweet_url': tweet_url
        }, ensure_ascii=False), 200
        
    except Exception as e:
        return json.dumps({
            'error': str(e)
        }, ensure_ascii=False), 500
