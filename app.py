from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent

#Deal with http request
import requests
import json

#Using SQLite
import sqlite3

app = Flask(__name__)

configuration = Configuration(access_token='AvD/A7ujeUf4cuqk0SxzRsuxCP6gZBlLMCiTytV93QeEHy5oI5+5jC+V4Fv/HUBZ4tUsT5c7P7NpwSkefhDkXWFpouVtvZBM4BN+jz7yIoK6w8vJNBPxUhVUBr2Mi+5zOxeMV6CdKIRlEXjRphI6tAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('9e76186debf867c540a0ad297893824b')

# Get message from Line
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):

    # Check if searched ID mapping with DB
    try:
        lower_text = event.message.text.lower()
        with sqlite3.connect("scam_line_ID.db") as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT line_ID FROM scam_line_ID WHERE line_ID = ?', (lower_text,))
            match = cursor.fetchone()
            if match:
                reply = "請留意！此帳戶為詐騙帳戶，切勿上當受騙。"
            else:
                reply = "此帳戶非註冊在案之詐騙帳戶。"
    except sqlite3.Error as e:
        reply = "出現錯誤，請稍後再試一次。錯誤代碼：" + str(e)

    # Send message back to user        
    url = "https://api.line.me/v2/bot/message/push"
    data = {
        "to": event.source.user_id,
        "messages": [
            {
                "type": "text",
                "text": reply
            }
        ]
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer AvD/A7ujeUf4cuqk0SxzRsuxCP6gZBlLMCiTytV93QeEHy5oI5+5jC+V4Fv/HUBZ4tUsT5c7P7NpwSkefhDkXWFpouVtvZBM4BN+jz7yIoK6w8vJNBPxUhVUBr2Mi+5zOxeMV6CdKIRlEXjRphI6tAdB04t89/1O/w1cDnyilFU="
    }

    response = requests.post(url, headers = headers, json = data)

    #with ApiClient(configuration) as api_client:
    #    line_bot_api = MessagingApi(api_client)

        #To see sender info.
        # print("event.reply_token:", event.reply_token)
        # print("event.source.user_id:", event.source.user_id)
        # print("event.message.text:", event.message.text)
        # print("event.reply_token", event.reply_token)

        # line_bot_api.reply_message_with_http_info(
        #     ReplyMessageRequest(
        #         reply_token=event.reply_token,
        #         messages=[TextMessage(text=event.message.text)]
        #     )
        # )

if __name__ == "__main__":
    app.run()