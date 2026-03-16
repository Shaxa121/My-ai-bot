import telebot
import os
from flask import Flask
from threading import Thread

# Config faylingizdan faqat tokenni olamiz
try:
    from config import config
    token = config.BOT_TOKEN
except:
    token = "7854228914:AAH_fL_Mv9vBvXjK0qG1w3yT9rA4sU5xI2o"

bot = telebot.TeleBot(token)
app = Flask('')

@app.route('/')
def home(): return "Bot is Online!"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🚀 Master AI Infinity ishga tushdi! Men tayyorman, Shaxzod.")

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    print("Bot polling boshlandi...")
    bot.infinity_polling()
