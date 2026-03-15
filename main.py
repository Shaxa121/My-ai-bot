import telebot
import requests
import time
import os
import logging
import sys
from threading import Thread
from flask import Flask

# --- SOZLAMALAR ---
TOKEN = '8780847488:AAGzf7a3CbKf5U88d8yEkUADLb8E8LuQvus'
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

# Render uchun Veb-server (Majburiy qism)
app = Flask(__name__)
@app.route('/')
def home():
    return "PRO AI Bot Render'da 100% faol!", 200

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Logging (Render Logs bo'limida nima bo'layotganini ko'rish uchun)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- AI KLASSI ---
class SmartAI:
    def __init__(self):
        self.url = "https://www.blackbox.ai/api/chat"
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

    def get_answer(self, prompt, attempt=1):
        if attempt > 3:
            return "Kechirasiz, AI serverlari band. Keyinroq urinib ko'ring. 😔"
        try:
            payload = {
                "messages": [{"role": "user", "content": prompt}],
                "model": "deepseek-v3",
                "max_tokens": 2048
            }
            logger.info(f"AI'ga so'rov ketdi... (Urinish: {attempt})")
            response = requests.post(self.url, json=payload, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                text = response.text
                clean_text = text.split('$@$')[0].strip() if '$@$' in text else text.strip()
                return clean_text if clean_text else "Javob bo'sh keldi."
            else:
                logger.warning(f"AI Xatosi: {response.status_code}. Qayta urinish...")
        except Exception as e:
            logger.error(f"Ulanish xatosi: {e}")
            
        time.sleep(2)
        return self.get_answer(prompt, attempt + 1)

ai = SmartAI()

# --- BOT KOMANDALARI ---
@bot.message_handler(commands=['start', 'help'])
def welcome(message):
    bot.reply_to(message, "🤖 *PRO AI Bot Render'da ishga tushdi!*\n\nSavolingizni bering:")

@bot.message_handler(func=lambda m: True)
def chat(message):
    bot.send_chat_action(message.chat.id, 'typing')
    start_time = time.time()
    
    answer = ai.get_answer(message.text)
    
    duration = round(time.time() - start_time, 1)
    footer = f"\n\n_⏱ {duration} soniyada javob berildi_"
    
    try:
        if len(answer) > 4000:
            for i in range(0, len(answer), 4000):
                bot.send_message(message.chat.id, answer[i:i+4000])
        else:
            bot.reply_to(message, answer + footer)
    except:
        bot.send_message(message.chat.id, answer) # Xato bo'lsa oddiy yuboradi

# --- ISHGA TUSHIRISH ---
if __name__ == "__main__":
    # 1. Render talab qilgan veb-serverni alohida fonda yoqamiz
    Thread(target=run_web).start()
    
    # 2. Telegramdagi 409 xatolarni tozalaymiz
    logger.info("Eski ulanishlar tozalanmoqda...")
    bot.remove_webhook()
    time.sleep(3)
    
    # 3. Botni uzluksiz ishga tushiramiz
    while True:
        try:
            logger.info("Bot Telegram'ga ulandi va xabar kutyapti!")
            bot.polling(none_stop=True, interval=0, timeout=60)
        except Exception as e:
            logger.error(f"Polling xatosi: {e}")
            time.sleep(5)
