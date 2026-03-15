import telebot, requests, os, time
from threading import Thread
from flask import Flask
from datetime import datetime

# --- KONFIGURATSIYA ---
TOKEN = '8780847488:AAFC_6Hk9CeHNdDkKTmurm-bxAq047K3G0I'
GEMINI_API_KEY = 'AIzaSyD9ARBdXpg-shwQWwhqTIR4T7KPmvR2Hmk'

bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")
app = Flask(__name__)

# Foydalanuvchi xotirasi (Chat History)
# {user_id: [messages]} ko'rinishida saqlaydi
user_memory = {}

@app.route('/')
def home(): return "GEMINI WITH MEMORY: ONLINE", 200

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

# --- GEMINI LOGIKASI ---
class SmartGemini:
    def __init__(self):
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        self.headers = {'Content-Type': 'application/json'}

    def ask(self, user_id, text):
        # 1. Haqiqiy vaqtni olish
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 2. Xotirani tekshirish (agar yangi foydalanuvchi bo'lsa)
        if user_id not in user_memory:
            user_memory[user_id] = []
        
        # 3. System Prompt (Botga kimligini eslatish)
        history_context = [
            {"role": "user", "parts": [{"text": f"Sen aqlli yordamchisan. Hozirgi sana va vaqt: {now}. O'zbek tilida gaplashasan va avvalgi suhbatimizni eslab qolishing kerak."}]},
            {"role": "model", "parts": [{"text": "Tushundim, suhbatni eslab qolaman va vaqtni inobatga olaman. Qanday yordam bera olaman?"}]}
        ]
        
        # 4. Foydalanuvchi xotirasini qo'shish (oxirgi 10 ta xabar)
        history_context.extend(user_memory[user_id][-10:])
        
        # 5. Yangi savolni qo'shish
        history_context.append({"role": "user", "parts": [{"text": text}]})

        try:
            payload = {
                "contents": history_context,
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 2048
                }
            }
            res = requests.post(self.url, json=payload, headers=self.headers, timeout=30)
            
            if res.status_code == 200:
                ans = res.json()['candidates'][0]['content']['parts'][0]['text']
                
                # 6. Xabarlarni xotiraga saqlash
                user_memory[user_id].append({"role": "user", "parts": [{"text": text}]})
                user_memory[user_id].append({"role": "model", "parts": [{"text": ans}]})
                
                return ans
            else:
                return f"⚠️ API xatosi: {res.status_code}"
        except Exception as e:
            return "❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring."

ai = SmartGemini()

# --- HANDLERS ---
@bot.message_handler(commands=['start', 'clear'])
def start_cmd(m):
    if m.text == '/clear':
        user_memory[m.from_user.id] = []
        bot.reply_to(m, "🧹 **Xotira tozalandi!** Endi suhbatni yangidan boshlashimiz mumkin.")
    else:
        bot.reply_to(m, "🌟 **Salom! Men xotiraga ega Master AI botman.**\n\nMen avvalgi gaplaringizni eslab qolaman va vaqtni bilaman. Savol bering!")

@bot.message_handler(func=lambda m: True)
def handle_msg(m):
    bot.send_chat_action(m.chat.id, 'typing')
    
    # User ID va matnni yuboramiz
    response = ai.ask(m.from_user.id, m.text)
    
    try:
        if len(response) > 4000:
            for x in range(0, len(response), 4000):
                bot.send_message(m.chat.id, response[x:x+4000])
        else:
            bot.reply_to(m, response)
    except Exception:
        bot.send_message(m.chat.id, response)

if __name__ == "__main__":
    Thread(target=run_web).start()
    bot.remove_webhook()
    bot.polling(none_stop=True)
