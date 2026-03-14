import telebot
import requests
import os
import time
from flask import Flask
from threading import Thread

# TOKENINGIZNI TEKSHIRIB QO'YING
TOKEN = '8728653741:AAEv9k3NdQfnaFtxfMY8pxrE1l3kEQC_zlk'
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)
@app.route('/')
def h(): return "OK", 200

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def get_ai(text):
    try:
        # Blackbox o'rniga vaqtincha juda sodda API
        res = requests.get(f"https://api.simsimi.vn/v2/?text={text}&lc=uz")
        return res.json()['result']
    except: return "Aloqa biroz yomon, qayta yozing."

@bot.message_handler(func=lambda m: True)
def hdl(m):
    bot.send_chat_action(m.chat.id, 'typing')
    bot.reply_to(m, get_ai(m.text))

if __name__ == "__main__":
    Thread(target=run).start()
    # MUHIM: Har qanday eski ulanishni majburan uzish
    bot.remove_webhook()
    time.sleep(2)
    print("BOT ISHLADI!")
    bot.polling(none_stop=True)
