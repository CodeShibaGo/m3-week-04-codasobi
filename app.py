from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv('YOUR_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('YOUR_CHANNEL_SECRET'))

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.route('/', methods=['GET'])
def home():
    return 'WELCOME TO HOME PAGE'

def generate_response(prompt, role="user"):
    instruction = "You are Gojo Satoru, a famous chracter in manga jujutsukaisen, please use his speaking style, which is full of humor and confident"
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": instruction},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text.lower()
    # echo msg
    if msg.startswith('/echo '):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=msg[6:])
        )
    # chatgbt
    elif msg.startswith('/ask '):
        completion = generate_response(msg[5:])
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=completion)
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='This is out of my knowledge, sorry')
        )

if __name__ == "__main__":
    app.run(debug=True)