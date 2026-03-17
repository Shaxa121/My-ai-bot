import telebot
import groq
import os
from flask import Flask
from threading import Thread

# --- YANGI TOKEN VA SOZLAMALAR ---
TOKEN = "8780847488:AAH75r9SwIrXUeCcfe-lKgdwljuu45eUx00"
GROQ_KEY = "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"

bot = telebot.TeleBot(TOKEN)
client = groq.Client(api_key=GROQ_KEY)
app = Flask('')

@app.route('/')
def home():
    return "<h1>Master AI Infinity is Online!</h1>"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🚀 Assalomu alaykum Shaxzod! Yangi tizim muvaffaqiyatli ishga tushdi. Men tayyorman!")

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
        bot.reply_to(message, f"❌ Xatolik yuz berdi: {str(e)}")

def run():
    # Render uchun port 8080
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    print("Bot yashil chiroqda...")
    bot.infinity_polling()
