import os
import requests
from flask import Flask, request

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
DEEPSEEK_API_KEY = os.environ["DEEPSEEK_API_KEY"]

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"


def send_message(chat_id, text):
    requests.post(
        f"{TELEGRAM_URL}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text
        },
        timeout=60
    )


def ask_deepseek(text):
    response = requests.post(
        DEEPSEEK_URL,
        headers={
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个友好的中文 AI 助手。"
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            "stream": False
        },
        timeout=120
    )

    response.raise_for_status()
    data = response.json()

    return data["choices"][0]["message"]["content"]


@app.route("/", methods=["GET"])
def home():
    return "Telegram DeepSeek Bot is running!"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)

    if not data:
        return "OK"

    message = data.get("message", {})
    chat = message.get("chat", {})
    text = message.get("text")

    if not chat or not text:
        return "OK"

    chat_id = chat["id"]

    try:
        answer = ask_deepseek(text)
        send_message(chat_id, answer)
    except Exception as e:
        print(e)
        send_message(chat_id, "抱歉，AI 暂时出错了，请稍后再试。")

    return "OK"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
