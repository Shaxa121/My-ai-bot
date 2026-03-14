import telebot
import requests
import os
from flask import Flask
from threading import Thread

# --- SOZLAMALAR ---
TELEGRAM_TOKEN = '8780847488:AAE6QJNOXrKiFZdRbKQOb1STnSHC2Lem8to'
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# --- RENDER UCHUN SERVER ---
app = Flask(__name__)

@app.route('/')
def health():
    return "Bot is Alive", 200

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- AI FUNKSIYASI (API KALIT SHART EMAS) ---
def get_ai_response(text):
    try:
        # Bu API tekin va cheksiz
        url = f"https://api.pawan.krd/cosmosrp/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        data = {
            "model": "cosmosrp",
            "messages": [{"role": "user", "content": text + " (javobni o'zbek tilida ber)"}]
        }
        # Agar bu ishlamasa, SimSimi zaxira variant
        res = requests.post(url, json=data, timeout=10)
        return res.json()['choices'][0]['message']['content']
    except:
        try:
            res = requests.get(f"https://api.simsimi.vn/v2/?text={text}&lc=uz")
            return res.json()['result']
        except:
            return "Hozircha javob berolmayman, birozdan keyin urinib ko'ring."

# --- BOT BUYRUQLARI ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f"Salom {message.from_user.first_name}! Men yangi AI modelman. Savolingizni bering!")

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    msg = message.text
    if msg.lower().startswith("rasm:"):
        prompt = msg[5:].strip()
        bot.send_photo(message.chat.id, f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}")
    else:
        bot.send_chat_action(message.chat.id, 'typing')
        answer = get_ai_response(msg)
        bot.reply_to(message, answer)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
