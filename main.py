import telebot
import os
from flask import Flask
from threading import Thread

# Tokenni to'g'ridan-to'g'ri shu yerga yozamiz (Xato bo'lmasligi uchun)
TOKEN = "7854228914:AAH_fL_Mv9vBvXjK0qG1w3yT9rA4sU5xI2o"

bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "Master AI is Active!"

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🚀 Shaxzod, botingiz 100% ishga tushdi!")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Men xabarni oldim! Tizim ishlayapti.")

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    print("Bot polling boshlandi...")
    bot.infinity_polling()
