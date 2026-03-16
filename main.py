import telebot
import os
import time
import logging
from flask import Flask
from threading import Thread
from config import config

# 1. LOGGING (Diagnostika asosi)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MasterInfinity")

# 2. WEB SERVER (Renderda 24/7 ishlash uchun)
server = Flask('')

@server.route('/')
def home():
    return "Master AI Infinity is Online!"

def run_server():
    server.run(host='0.0.0.0', port=config.PORT)

# 3. BOTNI ISHGA TUSHIRISH
bot = telebot.TeleBot(config.BOT_TOKEN)

# 4. MODULLARNI CHAQRISH (Keyingi fayllar tayyor bo'lgach ishlaydi)
# try:
#     from brain import brain
#     from social_media_beast import beast
#     from system_guardian import guardian
# except ImportError as e:
#     logger.warning(f"Ba'zi modullar hali yuklanmagan: {e}")

# 5. ASOSIY KOMANDALAR
@bot.message_handler(commands=['start'])
def start_cmd(message):
    welcome_msg = (
        f"Assalomu alaykum, {message.from_user.first_name}! 👋\n\n"
        "Men **Master AI Infinity** botiman. Sizning vaxshiy yordamchingiz! 🚀\n"
        "Menda hamma narsa bor: AI, Video Yuklovchi, Tarjimon va boshqalar.\n\n"
        "Qanday yordam bera olaman?"
    )
    bot.reply_to(message, welcome_msg, parse_mode="Markdown")

# 6. UNIVERSAL XABAR ISHLOVCHI (Mantiqiy markaz)
@bot.message_handler(func=lambda message: True)
def router(message):
    text = message.text
    user_id = message.chat.id

    if "instagram.com" in text or "tiktok.com" in text or "youtube.com" in text:
        bot.send_message(user_id, "🎬 Link aniqlandi! Video yuklash moduli ishga tushdi...")
        # beast.handle_download(message, bot)
    else:
        bot.send_chat_action(user_id, 'typing')
        # response = brain.get_response(user_id, text)
        bot.send_message(user_id, "🧠 AI tahlil qilmoqda... (Modul ulanmoqda)")

# 7. TIZIMNI YURGIZISH
if __name__ == "__main__":
    logger.info("Bot Renderda ishga tushmoqda...")
    Thread(target=run_server).start()
    bot.infinity_polling()
