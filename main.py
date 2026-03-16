import telebot
import os
import logging
from flask import Flask
from threading import Thread
from datetime import datetime

# 1. HAMMA MODULLARNI BIRLASHTIRISH (Import qismi)
from config import config
from brain import brain
from social_media_beast import beast
from weather_engine import weather
from islamic_core import islamic
from shazam_engine import shazam
from system_guardian import guardian
from vision_handler import vision
from universal_translator import translator
from memory_core import memory
from admin_panel import admin_p

# 2. LOGGING VA SERVER SOZLAMALARI
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MasterInfinity")
app = Flask('')

@app.route('/')
def home():
    return f"Master AI Infinity is Online! Status: Healthy. Time: {datetime.now()}"

def run_web_server():
    app.run(host='0.0.0.0', port=config.PORT)

# 3. BOTNI ISHGA TUSHIRISH
bot = telebot.TeleBot(config.BOT_TOKEN)

# 4. START KOMANDASI
@bot.message_handler(commands=['start'])
def welcome(message):
    memory.update_user(message.chat.id, message.from_user.username)
    welcome_text = (
        f"Assalomu alaykum, {message.from_user.first_name}! 🚀\n"
        "Siz **Master AI Infinity (Beast Edition)** tizimiga ulandingiz.\n\n"
        "Men nimalar qila olaman?\n"
        "🧠 AI Suhbat (Llama 3.3)\n"
        "🎬 Video Yuklovchi (Insta/TikTok/YT)\n"
        "🌦 Ob-havo va 🕋 Namoz vaqtlari\n"
        "👁 Rasm tahlili va 🌍 Tarjima\n\n"
        "Marhamat, menga biron nima yozing!"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

# 5. ADMIN PANEL (Faqat siz uchun)
@bot.message_handler(commands=['admin'])
def admin_access(message):
    if admin_p.is_admin(message.chat.id):
        stats = admin_p.get_stats()
        bot.reply_to(message, stats, parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ Bu buyruq faqat Shaxzod uchun!")

# 6. UNIVERSAL ROUTER (Asosiy Mantiq)
@bot.message_handler(content_types=['text', 'photo', 'voice'])
def handle_all_messages(message):
    user_id = message.chat.id
    
    try:
        # TEXT ISHLASH
        if message.content_type == 'text':
            text = message.text
            
            # Link bo'lsa - Video yuklash
            if any(link in text for link in ["instagram.com", "tiktok.com", "youtube.com", "youtu.be"]):
                bot.send_message(user_id, "🎬 Video yuklanmoqda, kuting...")
                file_path, title = beast.download_video(text)
                if file_path:
                    bot.send_video(user_id, open(file_path, 'rb'), caption=f"✅ {title}")
                    beast.clean_up(file_path)
                else:
                    bot.send_message(user_id, "❌ Yuklashda xatolik: Video juda katta yoki link noto'g'ri.")
            
            # Ob-havo so'ralsa
            elif "havo" in text.lower():
                bot.send_message(user_id, weather.get_weather("Bukhara"))
                
            # Namoz vaqtlari
            elif "namoz" in text.lower():
                bot.send_message(user_id, islamic.get_prayer_times("Bukhara"))

            # Aks holda - AI suhbat
            else:
                bot.send_chat_action(user_id, 'typing')
                ai_reply = brain.get_ai_response(user_id, text)
                bot.send_message(user_id, ai_reply, parse_mode="Markdown")

        # RASYM ISHLASH (Vision)
        elif message.content_type == 'photo':
            bot.send_message(user_id, "👁 Rasmni ko'ryapman, tahlil qilmoqdaman...")
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            with open("vision_input.jpg", 'wb') as new_file:
                new_file.write(downloaded_file)
            
            analysis = vision.analyze_image("vision_input.jpg")
            bot.reply_to(message, analysis)

    except Exception as e:
        error_msg = guardian.report_error(str(e))
        bot.send_message(config.ADMIN_ID, error_msg)
        bot.send_message(user_id, "😔 Tizimda nosozlik bo'ldi. Admin ogohlantirildi.")

# 7. TIZIMNI YURGIZISH
if __name__ == "__main__":
    logger.info("Master AI Infinity ishga tushdi!")
    Thread(target=run_web_server).start()
    bot.infinity_polling()
