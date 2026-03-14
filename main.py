import telebot
import requests
import os
from flask import Flask
from threading import Thread

# --- SOZLAMALAR ---
TELEGRAM_TOKEN = '8780847488:AAE6QJNOXrKiFZdRbKQOb1STnSHC2Lem8to'
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# --- RENDERNI ALDASH UCHUN SERVER ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "OK", 200

def run():
    # Render aynan shu PORTni kutadi
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- BOT FUNKSIYALARI ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Salom! Men ishlayapman. Savol yuboring!")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    msg = message.text
    if msg.lower().startswith("rasm:"):
        prompt = msg[5:].strip()
        bot.send_photo(message.chat.id, f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}")
    else:
        try:
            res = requests.get(f"https://api.simsimi.vn/v2/?text={msg}&lc=uz")
            bot.reply_to(message, res.json()['result'])
        except:
            bot.reply_to(message, "Hozircha javob berolmayman...")

# --- ISHGA TUSHIRISH ---
if __name__ == "__main__":
    # Avval serverni yoqamiz
    server_thread = Thread(target=run)
    server_thread.start()
    
    print("Bot polling boshlandi...")
    bot.infinity_polling()
