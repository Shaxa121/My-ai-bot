import telebot
import groq
import os
import requests
from flask import Flask
from threading import Thread

# --- SOZLAMALAR ---
# Telegram bot tokeningiz
TOKEN = "8780847488:AAH75r9SwIrXUeCcfe-lKgdwljuu45eUx00"
# Groq AI API kaliti
GROQ_KEY = "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"
# Siz bergan yangi Ob-havo API kaliti
WEATHER_API_KEY = "10821781d7c51053fbef17b2da05dfba"

bot = telebot.TeleBot(TOKEN)
client = groq.Client(api_key=GROQ_KEY)
app = Flask('')

# Foydalanuvchi xotirasi (Suhbatni eslab qolish uchun)
user_memory = {}

# --- 🌤 OB-HAVO FUNKSIYASI ---
def get_weather_pro(city="Bukhara"):
    try:
        # OpenWeatherMap API orqali professional ma'lumot olish
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=uz"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data["cod"] == 200:
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            hum = data["main"]["humidity"]
            wind = data["wind"]["speed"]
            
            return (f"🌤 **{city} ob-havosi:**\n\n"
                    f"🌡 Harorat: {temp}°C\n"
                    f"☁️ Holat: {desc.capitalize()}\n"
                    f"💧 Namlik: {hum}%\n"
                    f"💨 Shamol: {wind} m/s")
        else:
            return "❌ Shahar topilmadi yoki API kalit hali aktivlashmagan."
    except Exception:
        return "❌ Ob-havo xizmati bilan bog'lanishda xato."

# --- 🌐 RENDER WEB SERVER ---
@app.route('/')
def home():
    return "<h1>Master AI Infinity is Online!</h1><p>Creator: Shaxzod</p>"

# --- 🤖 BOT BUYRUQLARI ---
@bot.message_handler(commands=['start'])
def start(message):
    welcome = (
        "🚀 **Assalomu alaykum Shaxzod!**\n\n"
        "Men Master AI Infinity botsan. Men endi ancha aqlliman:\n"
        "✅ Sizni taniyman va gaplarimizni eslayman.\n"
        "✅ Ob-havoni aniq aytib beraman.\n"
        "✅ AI orqali har qanday savolga javob beraman.\n\n"
        "Suhbatni boshlash uchun biror narsa yozing!"
    )
    bot.reply_to(message, welcome, parse_mode="Markdown")

# --- 🧠 ASOSIY MANTIQ (AI VA OB-HAVO) ---
@bot.message_handler(func=lambda message: True)
def handle_all(message):
    user_id = message.from_user.id
    text = message.text.lower()

    # 1. Ob-havo so'ralganini tekshirish
    if "ob-havo" in text or "weather" in text:
        bot.send_chat_action(message.chat.id, 'typing')
        # Standart Buxoro, lekin xohlasangiz shaharni o'zgartirish mumkin
        info = get_weather_pro("Bukhara")
        bot.reply_to(message, info, parse_mode="Markdown")
        return

    # 2. AI va Xotira mantiqi
    bot.send_chat_action(message.chat.id, 'typing')
    
    if user_id not in user_memory:
        user_memory[user_id] = []

    # Oxirgi 6 ta xabarni xotirada saqlash
    user_memory[user_id].append({"role": "user", "content": message.text})
    if len(user_memory[user_id]) > 6:
        user_memory[user_id] = user_memory[user_id][-6:]

    try:
        system_instruction = {
            "role": "system", 
            "content": "Sen Master AI Infinity botsan. Yaratuvchingning ismi Shaxzod. Doimo o'zbek tilida javob berasan."
        }
        
        full_context = [system_instruction] + user_memory[user_id]

        response = client.chat.completions.create(
            messages=full_context,
            model="llama-3.3-70b-versatile",
        )
        
        ai_reply = response.choices[0].message.content
        user_memory[user_id].append({"role": "assistant", "content": ai_reply})
        
        bot.reply_to(message, ai_reply)
        
    except Exception as e:
        bot.reply_to(message, f"❌ AI xatosi: {str(e)}")

# --- 🚀 SERVERNI YURGIZISH ---
def run_server():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

if __name__ == "__main__":
    t = Thread(target=run_server)
    t.start()
    print("Bot muvaffaqiyatli ishga tushdi!")
    bot.infinity_polling()
