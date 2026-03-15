import telebot, requests, os, time
from threading import Thread
from flask import Flask

# --- ASOSIY SOZLAMALAR ---
TOKEN = '8780847488:AAFC_6Hk9CeHNdDkKTmurm-bxAq047K3G0I'
# Siz bergan Groq API kaliti
GROQ_API_KEY = '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'

bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

# Render uchun majburiy veb-server
app = Flask(__name__)
@app.route('/')
def home(): return "SUPER-FAST AI STATUS: ONLINE", 200

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- GROQ AI LOGIKASI ---
class GroqAI:
    def __init__(self):
        self.url = "https://api.groq.com/openai/v1/chat/completions"
        self.session = requests.Session()
        self.headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

    def ask(self, user_text):
        try:
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {
                        "role": "system", 
                        "content": "Sen universal professional yordamchisan. Har qanday fan (matematika, tarix, fizika) bo'yicha mukammal bilasan. O'zbek tilida juda tez va aniq javob ber."
                    },
                    {"role": "user", "content": user_text}
                ],
                "temperature": 0.6,
                "max_tokens": 2048
            }
            # Groq juda tez bo'lgani uchun timeoutni 20 soniya qo'yamiz
            res = self.session.post(self.url, json=payload, headers=self.headers, timeout=20)
            
            if res.status_code == 200:
                return res.json()['choices'][0]['message']['content'].strip()
            else:
                return f"⚠️ API xatosi (Status: {res.status_code})"
        except Exception as e:
            return "❌ Ulanishda xatolik yuz berdi. Birozdan so'ng qayta urinib ko'ring."

ai = GroqAI()

# --- BOT KOMANDALARI ---
@bot.message_handler(commands=['start'])
def start(m):
    welcome_msg = (
        "🚀 *Super-Fast AI Botga xush kelibsiz!*\n\n"
        "Men hozirda eng tezkor **Groq LPU** chiplarida ishlayapman.\n"
        "Savolingizni bering, men srazu javob beraman!"
    )
    bot.send_message(m.chat.id, welcome_msg)

@bot.message_handler(func=lambda m: True)
def handle(m):
    # 'typing' holatini yuboramiz
    bot.send_chat_action(m.chat.id, 'typing')
    
    # AI dan javobni olish
    response = ai.ask(m.text)
    
    # Telegram xabar limiti (4096 belgi) bo'yicha bo'lib yuborish
    try:
        if len(response) > 4000:
            for x in range(0, len(response), 4000):
                bot.send_message(m.chat.id, response[x:x+4000])
        else:
            bot.reply_to(m, response)
    except Exception as e:
        # Markdown xatosi bo'lsa, oddiy matn sifatida yuboradi
        bot.send_message(m.chat.id, response)

# --- ISHGA TUSHIRISH ---
if __name__ == "__main__":
    # 1. Serverni fonda yoqish
    Thread(target=run_web).start()
    
    # 2. Konfliktlarni tozalash
    bot.remove_webhook()
    time.sleep(1)
    
    # 3. Uzluksiz polling
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=40)
        except Exception:
            time.sleep(5)
