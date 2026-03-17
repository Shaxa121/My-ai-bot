import telebot
import groq
import os
from flask import Flask
from threading import Thread

# --- SOZLAMALAR ---
TOKEN = "7854228914:AAH_fL_Mv9vBvXjK0qG1w3yT9rA4sU5xI2o"
GROQ_KEY = "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"

bot = telebot.TeleBot(TOKEN)
client = groq.Client(api_key=GROQ_KEY)
app = Flask('')

# --- RENDER UCHUN PORT ---
@app.route('/')
def home():
    return "Bot Online!"

# --- BOT MANTIQI ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🚀 Master AI Infinity ishga tushdi! Men tayyorman, Shaxzod.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # AI dan javob olish
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Sen Master AI Infinity botsan. O'zbek tilida javob ber."},
                {"role": "user", "content": message.text}
            ]
        )
        reply = completion.choices[0].message.content
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, f"🧠 AI tizimida xato: {str(e)}")

# --- YOQISH ---
def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

if __name__ == "__main__":
    # Flask serverni alohida yo'lakda yoqamiz
    Thread(target=run).start()
    print("Bot polling boshlandi...")
    # Botni asosiy yo'lakda yoqamiz
    bot.infinity_polling()
