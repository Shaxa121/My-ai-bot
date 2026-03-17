import telebot
import groq
import os
from flask import Flask
from threading import Thread

# --- SOZLAMALAR ---
# Telegram bot tokeningiz (Oxirgi berganingiz)
TOKEN = "8780847488:AAH75r9SwIrXUeCcfe-lKgdwljuu45eUx00"

# Groq API kaliti (Yangi berganingiz)
GROQ_KEY = "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"

bot = telebot.TeleBot(TOKEN)
client = groq.Client(api_key=GROQ_KEY)
app = Flask('')

@app.route('/')
def home():
    return "<h1>Master AI Infinity is Active!</h1>"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🚀 Master AI Infinity ishga tushdi! Men tayyorman, Shaxzod.")

@bot.message_handler(func=lambda message: True)
def handle_ai(message):
    try:
        # AI dan javob olish
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Sen Master AI botsan. O'zbek tilida javob berasan."},
                {"role": "user", "content": message.text}
            ],
            model="llama-3.3-70b-versatile",
        )
        bot.reply_to(message, chat_completion.choices[0].message.content)
    except Exception as e:
        bot.reply_to(message, f"❌ AI xatosi: {str(e)}")

def run():
    # Render uchun 8080 porti
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

if __name__ == "__main__":
    # Flaskni alohida yo'lakda (thread) ishga tushiramiz
    t = Thread(target=run)
    t.start()
    print("Bot xabarlarni kutmoqda...")
    bot.infinity_polling()
