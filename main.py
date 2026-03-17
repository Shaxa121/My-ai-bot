import telebot
import groq
import os
from flask import Flask
from threading import Thread
from weather import get_weather  # weather.py faylimizdan funksiyani chaqiramiz

# --- SOZLAMALAR ---
TOKEN = "8780847488:AAH75r9SwIrXUeCcfe-lKgdwljuu45eUx00"
GROQ_KEY = "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"

bot = telebot.TeleBot(TOKEN)
client = groq.Client(api_key=GROQ_KEY)
app = Flask('')

# Foydalanuvchi xotirasi (Suhbat davomiyligini ta'minlash uchun)
user_memory = {}

@app.route('/')
def home():
    return "<h1>Master AI Infinity is running perfectly!</h1><p>Created by Shaxzod</p>"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    text = (
        "🚀 **Master AI Infinity-ga xush kelibsiz!**\n\n"
        "Men Shaxzod tomonidan yaratilgan aqlli yordamchiman.\n"
        "Siz bilan suhbatlashaman, sizni taniyman va ob-havoni ayta olaman.\n\n"
        "💡 *Maslahat:* 'Ob-havo qanday?' deb so'rab ko'ring."
    )
    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    user_text = message.text.lower()

    # 1-QADAM: Ob-havo buyrug'ini tekshirish
    if "ob-havo" in user_text or "weather" in user_text:
        bot.send_chat_action(message.chat.id, 'typing')
        # Standart Buxoro, lekin foydalanuvchi boshqa shahar yozsa ham bo'ladi
        result = get_weather("Bukhara") 
        bot.reply_to(message, result, parse_mode="Markdown")
        return

    # 2-QADAM: AI va Xotira mantiqi
    bot.send_chat_action(message.chat.id, 'typing')
    
    if user_id not in user_memory:
        user_memory[user_id] = []

    # Xabarni xotiraga qo'shish (oxirgi 6 ta xabar)
    user_memory[user_id].append({"role": "user", "content": message.text})
    if len(user_memory[user_id]) > 6:
        user_memory[user_id] = user_memory[user_id][-6:]

    try:
        # AI ga ko'rsatma berish
        system_prompt = {
            "role": "system", 
            "content": "Sen Master AI Infinity botsan. Yaratuvchingning ismi Shaxzod. Doimo o'zbek tilida javob ber. Aqlli va do'stona bo'l."
        }
        
        full_context = [system_prompt] + user_memory[user_id]

        response = client.chat.completions.create(
            messages=full_context,
            model="llama-3.3-70b-versatile",
        )
        
        ai_reply = response.choices[0].message.content
        user_memory[user_id].append({"role": "assistant", "content": ai_reply})
        
        bot.reply_to(message, ai_reply)
        
    except Exception as e:
        bot.reply_to(message, "🧠 AI biroz charchadi. Iltimos, bir ozdan keyin urinib ko'ring.")

def run_server():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

if __name__ == "__main__":
    # Flaskni fonda ishga tushiramiz
    t = Thread(target=run_server)
    t.start()
    print("Bot ishga tushdi...")
    bot.infinity_polling()
