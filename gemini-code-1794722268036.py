import os
import requests

def send_to_slack(message: str):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        return
    res = requests.post(webhook_url, json={"text": message})
    print(f"📩 Slack通知ステータス: {res.status_code}")

def send_to_line(message: str):
    """LINE Messaging API（Push通知）を使用して自分のLINEに送信"""
    token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    user_id = os.getenv("LINE_USER_ID")
    if not token or not user_id:
        return
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    # LINEの1メッセージ上限（5000文字）に収める
    payload = {
        "to": user_id,
        "messages": [{"type": "text", "text": message[:4900]}]
    }
    res = requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=payload)
    print(f"📩 LINE通知ステータス: {res.status_code}")

def send_to_custom_app_webhook(result_payload: dict):
    """あなたが開発中のモバイルアプリやバックエンドAPIへJSONデータを直接POSTする"""
    app_webhook = os.getenv("CUSTOM_APP_WEBHOOK_URL")
    if not app_webhook:
        return
    res = requests.post(app_webhook, json=result_payload)
    print(f"📱 自作アプリAPI送信ステータス: {res.status_code}")

def dispatch_notifications(result_payload: dict):
    thought_summary = "\n".join([f"・{log}" for log in result_payload["thought_process"]])
    
    formatted_text = (
        f"🚀 *【AETHER-AUTONOMOUS 自律思考レポート】*\n"
        f"日時: {result_payload['timestamp']} | 最終到達スコア: *{result_payload['final_score']}点*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{result_payload['final_idea']}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🧠 *【AIの思考・自己批判プロセス】*\n{thought_summary}"
    )

    send_to_slack(formatted_text)
    send_to_line(formatted_text)
    send_to_custom_app_webhook(result_payload)