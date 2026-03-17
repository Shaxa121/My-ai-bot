import telebot
import groq
import os
import requests
from flask import Flask
from threading import Thread

# --- SOZLAMALAR ---
TOKEN = "8780847488:AAH75r9SwIrXUeCcfe-lKgdwljuu45eUx00"
GROQ_KEY = "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"

bot = telebot.TeleBot(TOKEN)
client = groq.Client(api_key=GROQ_KEY)
app = Flask('')

# Foydalanuvchi xotirasi
user_memory = {}

# --- OB-HAVO FUNKSIYASI (Shu yerning o'zida) ---
def get_weather_local(city="Bukhara"):
    try:
        url = f"https://wttr.in/{city}?format=%c+%t+%C+Namlik:+%h&lang=uz"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return f"🌤 **{city} ob-havosi:**\n\n{response.text}"
        return "❌ Ob-havo ma'lumotini olib bo'lmadi."
    except:
        return "❌ Ob-havo xizmati ishlamayapti."

# --- RENDER WEB SERVER ---
@app.route('/')
def home():
    return "<h1>Master AI Infinity is Active!</h1>"

# --- BOT BUYRUQLARI ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🚀 Salom Shaxzod! Men tayyorman. Ob-havo uchun 'ob-havo' deb yozing.")

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    user_id = message.from_user.id
    text = message.text.lower()

    # 1. Ob-havo qismi
    if "ob-havo" in text or "weather" in text:
        bot.send_chat_action(message.chat.id, 'typing')
        info = get_weather_local("Bukhara")
        bot.reply_to(message, info, parse_mode="Markdown")
        return

    # 2. AI va Xotira qismi
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
        bot.reply_to(message, "🧠 AI tizimida kichik uzilish.")

# --- SERVERNI YOQISH ---
def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.infinity_polling()
