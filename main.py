import telebot
import groq
import os
from flask import Flask
from threading import Thread
# DIQQAT: Funksiya nomi weather.py dagi bilan bir xil bo'lishi shart!
from weather import get_weather_data 

# --- SOZLAMALAR ---
TOKEN = "8780847488:AAH75r9SwIrXUeCcfe-lKgdwljuu45eUx00"
GROQ_KEY = "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"

bot = telebot.TeleBot(TOKEN)
client = groq.Client(api_key=GROQ_KEY)
app = Flask('')

user_memory = {}

@app.route('/')
def home():
    return "<h1>Master AI Infinity is Online!</h1>"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🚀 Salom Shaxzod! Men tayyorman. Ob-havoni so'rash uchun 'ob-havo' deb yozing.")

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    user_id = message.from_user.id
    text = message.text.lower()

    # 1. OB-HAVO QISMI
    if "ob-havo" in text or "weather" in text:
        bot.send_chat_action(message.chat.id, 'typing')
        # Bu yerda yangi nom ishlatilyapti:
        info = get_weather_data("Bukhara") 
        bot.reply_to(message, info, parse_mode="Markdown")
        return

    # 2. AI VA XOTIRA QISMI
    bot.send_chat_action(message.chat.id, 'typing')
    if user_id not in user_memory:
        user_memory[user_id] = []

    user_memory[user_id].append({"role": "user", "content": message.text})
    if len(user_memory[user_id]) > 6:
        user_memory[user_id] = user_memory[user_id][-6:]

    try:
        system_prompt = {"role": "system", "content": "Sen Master AI botsan. Yaratuvching Shaxzod. O'zbekcha javob ber."}
        full_context = [system_prompt] + user_memory[user_id]

        response = client.chat.completions.create(
            messages=full_context,
            model="llama-3.3-70b-versatile",
        )
        
        reply = response.choices[0].message.content
        user_memory[user_id].append({"role": "assistant", "content": reply})
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, "❌ AI tizimida kichik xatolik.")

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
