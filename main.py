import telebot
import requests
import os
from flask import Flask
from threading import Thread
from telebot import types

# --- SOZLAMALAR ---
TELEGRAM_TOKEN = '8780847488:AAE6QJNOXrKiFZdRbKQOb1STnSHC2Lem8to'
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# --- RENDER UCHUN SERVER (PORT XATOSINI YO'QOTISH) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    # Render avtomatik PORT beradi, agar bermasa 8080 ni oladi
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- AI FUNKSIYASI ---
def get_ai_answer(text):
    try:
        # SimSimi API (O'zbek tili uchun eng osoni)
        res = requests.get(f"https://api.simsimi.vn/v2/?text={text}&lc=uz")
        return res.json()['result']
    except:
        return "Hozircha tizimda yuklama ko'p. Birozdan keyin yozing!"

# --- TELEGRAM COMMANDS ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🤖 AI Chat"), types.KeyboardButton("🎨 Rasm"))
    bot.send_message(message.chat.id, f"Salom {message.from_user.first_name}! Bot tayyor. Savol yuboring yoki rasm chizdiring (rasm: ...)", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    msg = message.text
    if msg.lower().startswith("rasm:"):
        prompt = msg[5:].strip()
        bot.reply_to(message, "🎨 Rasm tayyorlanyapti, kuting...")
        image_url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}"
        bot.send_photo(message.chat.id, photo=image_url, caption=f"Natija: {prompt}")
    else:
        bot.send_chat_action(message.chat.id, 'typing')
        bot.reply_to(message, get_ai_answer(msg))

# --- ISHGA TUSHIRISH ---
if __name__ == "__main__":
    keep_alive() # Serverni orqa fonda yoqadi
    print("Bot ishga tushdi...")
    bot.infinity_polling()
