import telebot
import requests
import os
import time
from flask import Flask
from threading import Thread

# TOKENNI TEKSHIRING
TOKEN = '8728653741:AAEv9k3NdQfnaFtxfMY8pxrE1l3kEQC_zlk'
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Active", 200

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def get_ai(text):
    try:
        # Blackbox AI
        url = "https://api.blackbox.ai/api/chat"
        payload = {"messages": [{"role": "user", "content": text}], "model": "deepseek-v3"}
        res = requests.post(url, json=payload, timeout=15)
        return res.text.split('$@$')[0].strip()
    except:
        return "Xatolik bo'ldi, qayta urinib ko'ring."

@bot.message_handler(func=lambda m: True)
def handle(m):
    bot.send_chat_action(m.chat.id, 'typing')
    bot.reply_to(m, get_ai(m.text))

if __name__ == "__main__":
    # 1. Serverni yoqamiz
    Thread(target=run).start()
    
    # 2. Konfliktni oldini olish uchun muhim qism
    print("Eski ulanishlar tozalanmoqda...")
    bot.remove_webhook()
    time.sleep(3) # Renderga eski nusxani o'chirishga vaqt beramiz
    
    print("Bot muvaffaqiyatli ishga tushdi!")
    # 3. Pollingni boshlaymiz
    bot.polling(none_stop=True, interval=1, timeout=20)
