import telebot
import requests
import time
import os
import logging
from threading import Thread
from flask import Flask

# --- SOZLAMALAR ---
TOKEN = '8780847488:AAGzf7a3CbKf5U88d8yEkUADLb8E8LuQvus'
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

# Render uchun Veb-server (Majburiy)
app = Flask(__name__)
@app.route('/')
def home():
    return "Pollinations AI Bot Render'da 100% faol!", 200

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# --- YANGI, KALIT SO'RAMAYDIGAN AI ---
class SmartAI:
    def get_answer(self, prompt, attempt=1):
        if attempt > 3:
            return "Kechirasiz, ulanishda xatolik bo'ldi. Keyinroq urinib ko'ring. 😔"
        try:
            url = "https://text.pollinations.ai/"
            payload = {
                "messages": [
                    {"role": "system", "content": "Sen juda aqlli va yordamsevar botsan. Har doim O'zbek tilida, tushunarli javob berasan."},
                    {"role": "user", "content": prompt}
                ]
            }
            logger.info(f"So'rov yuborilmoqda... (Urinish: {attempt})")
            
            # Hech qanday Header yoki API kalit kerak emas!
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                return response.text.strip()
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
    bot.reply_to(message, "🤖 *Yangi AI Bot ishga tushdi!*\n\nMen hech qanday API kalitsiz ishlayman. Savolingizni bering:")

@bot.message_handler(func=lambda m: True)
def chat(message):
    bot.send_chat_action(message.chat.id, 'typing')
    start_time = time.time()
    
    answer = ai.get_answer(message.text)
    duration = round(time.time() - start_time, 1)
    
    try:
        if len(answer) > 4000:
            for i in range(0, len(answer), 4000):
                bot.send_message(message.chat.id, answer[i:i+4000])
        else:
            bot.reply_to(message, f"{answer}\n\n_⏱ {duration} soniyada_")
    except:
        bot.send_message(message.chat.id, answer)

# --- ISHGA TUSHIRISH ---
if __name__ == "__main__":
    Thread(target=run_web).start()
    
    logger.info("Eski ulanishlar tozalanmoqda...")
    bot.remove_webhook()
    time.sleep(3)
    
    while True:
        try:
            logger.info("Bot xabar kutmoqda...")
            bot.polling(none_stop=True, interval=0, timeout=60)
        except Exception as e:
            logger.error(f"Polling xatosi: {e}")
            time.sleep(5)
