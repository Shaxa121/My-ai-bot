import telebot, requests, time, os, logging
from threading import Thread
from flask import Flask

# --- KONFIGURATSIYA ---
TOKEN = '8780847488:AAFC_6Hk9CeHNdDkKTmurm-bxAq047K3G0I'
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

# Render uchun kichik veb-server
app = Flask(__name__)
@app.route('/')
def home(): return "PRO AI STATUS: ONLINE", 200

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- PRO AI LOGIKASI ---
class ProAI:
    def __init__(self):
        self.url = "https://text.pollinations.ai/"
        # Bu yerda botning "miyasiga" barcha fanlar bo'yicha bilim joylaymiz
        self.system_instruction = (
            "Sen universal Professional AI yordamchisan. Sening vazifang:\n"
            "1. Matematika: Misollarni bosqichma-bosqich yech.\n"
            "2. Tarix: Sanalar va voqealarni 100% aniqlik bilan ayt.\n"
            "3. Fan: Fizika, Kimyo va Biologiyadan ilmiy asoslangan javob ber.\n"
            "4. Til: O'zbek tilida grammatik xatosiz va chiroyli gaplash.\n"
            "Har doim aniq, ixcham va foydali ma'lumot ber."
        )

    def ask(self, user_text):
        try:
            payload = {
                "messages": [
                    {"role": "system", "content": self.system_instruction},
                    {"role": "user", "content": user_text}
                ],
                "model": "openai", # Eng aqlli modelni tanlaymiz
                "seed": 42 # Javoblar aniqligi uchun
            }
            res = requests.post(self.url, json=payload, timeout=40)
            return res.text.strip() if res.status_code == 200 else "Xatolik yuz berdi. Qayta urinib ko'ring."
        except:
            return "Server bilan aloqa uzildi. Birozdan so'ng yozing."

ai = ProAI()

# --- BOT FUNKSIYALARI ---
@bot.message_handler(commands=['start'])
def start(m):
    text = (
        "🎓 *Professional AI Tizimiga Xush Kelibsiz!*\n\n"
        "Men endi har qanday fan bo'yicha mutaxassisman:\n"
        "➕ *Matematika* (yechimlar bilan)\n"
        "📜 *Tarix* (aniq faktlar)\n"
        "🔬 *Fanlar* (fizika, kimyo)\n"
        "💻 *Dasturlash*\n\n"
        "Savolingizni yuboring!"
    )
    bot.send_message(m.chat.id, text)

@bot.message_handler(func=lambda m: True)
def handle(m):
    bot.send_chat_action(m.chat.id, 'typing')
    
    # AI dan javob olish
    response = ai.ask(m.text)
    
    # Javobni Telegram limiti bo'yicha tekshirish (4096 belgi)
    if len(response) > 4000:
        for x in range(0, len(response), 4000):
            bot.send_message(m.chat.id, response[x:x+4000])
    else:
        bot.reply_to(m, response)

# --- ISHGA TUSHIRISH ---
if __name__ == "__main__":
    Thread(target=run_web).start()
    logging.info("Bot ishga tushdi...")
    bot.remove_webhook()
    time.sleep(1)
    
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=60)
        except Exception as e:
            time.sleep(5)
