import telebot
import requests
import time
import os
import logging
from threading import Thread
from flask import Flask

# --- YANGI TOKEN ---
TOKEN = '8780847488:AAFC_6Hk9CeHNdDkKTmurm-bxAq047K3G0I'
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

# Render uchun Veb-server
app = Flask(__name__)
@app.route('/')
def home():
    return "AI Bot status: ACTIVE", 200

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# --- TAKOMILLASHTIRILGAN AI TIZIMI ---
class SmartAI:
    def get_answer(self, prompt, attempt=1):
        if attempt > 3:
            return "Kechirasiz, hozir bog'lanishda qiyinchilik bo'lyapti. 😔"
        try:
            url = "https://text.pollinations.ai/"
            # AI'ga aniqroq ko'rsatma (System Prompt) beramiz
            payload = {
                "messages": [
                    {
                        "role": "system", 
                        "content": "Sen aqlli, o'zbek tilida mukammal so'zlashuvchi AI botsan. Foydalanuvchi savollariga aniq, lirik chekinishlarsiz va foydali javob berasan."
                    },
                    {"role": "user", "content": prompt}
                ],
                "cache": True # Tezlikni oshirish uchun
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                answer = response.text.strip()
                if not answer:
                    return "AI bo'sh javob qaytardi, iltimos qayta yozing."
                return answer
            else:
                logger.warning(f"Xato kodi: {response.status_code}. Qayta urinish...")
        except Exception as e:
            logger.error(f"Xato: {e}")
            
        time.sleep(2)
        return self.get_answer(prompt, attempt + 1)

ai = SmartAI()

# --- BOT KOMANDALARI ---
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "🌟 *Aqlli AI botingiz tayyor!*\n\nYangi token o'rnatildi va tizim takomillashtirildi. Savolingizni bering:")

@bot.message_handler(func=lambda m: True)
def chat(message):
    # Foydalanuvchiga bot o'ylayotganini bildirish
    bot.send_chat_action(message.chat.id, 'typing')
    
    start_time = time.time()
    answer = ai.get_answer(message.text)
    duration = round(time.time() - start_time, 1)
    
    # Javobni chiroyli ko'rinishda yuborish
    try:
        if len(answer) > 4000:
            for i in range(0, len(answer), 4000):
                bot.send_message(message.chat.id, answer[i:i+4000])
        else:
            # Javob oxiriga vaqtni qo'shib qo'yamiz (Pro ko'rinish uchun)
            bot.reply_to(message, f"{answer}\n\n_⚡️ {duration}s_")
    except Exception as e:
        logger.error(f"Yuborishda xato: {e}")
        bot.send_message(message.chat.id, answer)

# --- ISHGA TUSHIRISH ---
if __name__ == "__main__":
    # Serverni alohida oqimda yoqamiz
    Thread(target=run_web).start()
    
    # 409 xatosini oldini olish
    bot.remove_webhook()
    time.sleep(2)
    
    while True:
        try:
            logger.info("Bot polling holatida...")
            bot.polling(none_stop=True, interval=0, timeout=60)
        except Exception as e:
            logger.error(f"Polling xatosi: {e}")
            time.sleep(5)
