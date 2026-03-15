import telebot, requests, os, time
from threading import Thread
from flask import Flask

# --- KONFIG ---
TOKEN = '8780847488:AAFC_6Hk9CeHNdDkKTmurm-bxAq047K3G0I'
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

# Render serverini minimal holatda saqlash
app = Flask(__name__)
@app.route('/')
def home(): return "OK", 200

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

# --- ULTRA TEZ AI KLASSI ---
class FlashAI:
    def __init__(self):
        self.url = "https://text.pollinations.ai/"
        # Session ulanishni doimiy ochiq saqlaydi (Keep-Alive)
        self.session = requests.Session()
        self.system = "Sen juda tezkor botsan. Qisqa va londa javob ber."

    def ask(self, text):
        try:
            # Mistral modeli hozirda eng tezkorlaridan biri
            payload = {
                "messages": [
                    {"role": "system", "content": self.system},
                    {"role": "user", "content": text}
                ],
                "model": "mistral", 
                "cache": True,
                "stream": False # Stream o'chiq bo'lsa, Render'da barqaror va tez keladi
            }
            # Timeoutni 10 soniyaga tushiramiz
            res = self.session.post(self.url, json=payload, timeout=10)
            return res.text.strip()
        except:
            return "Xatolik! Qayta urinib ko'ring."

ai = FlashAI()

@bot.message_handler(func=lambda m: True)
def handle(m):
    # 'typing' yuborishni olib tashladik (bu ham 0.5 soniya vaqt oladi)
    response = ai.ask(m.text)
    try:
        bot.reply_to(m, response)
    except:
        bot.send_message(m.chat.id, response)

if __name__ == "__main__":
    Thread(target=run_web).start()
    bot.remove_webhook()
    # Intervalni 0 qilib, pollingni maksimal tezlashtiramiz
    bot.polling(none_stop=True, interval=0, timeout=10)
