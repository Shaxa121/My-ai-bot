import telebot, requests, os, time
from threading import Thread
from flask import Flask
from datetime import datetime

# --- KONFIGURATSIYA ---
TOKEN = '8780847488:AAFC_6Hk9CeHNdDkKTmurm-bxAq047K3G0I'
# Yangi API kalitingiz joylandi
GEMINI_API_KEY = 'AIzaSyBxV4e1njS4O9jvegWFs7mVXEAxz039ReY'

bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")
app = Flask(__name__)

# Foydalanuvchi xotirasi (Chat History)
user_memory = {}

@app.route('/')
def home(): return "GEMINI PRO SYSTEM: ONLINE", 200

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

# --- GEMINI LOGIKASI ---
class MasterGemini:
    def __init__(self):
        # Eng barqaror v1beta API endpoint
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        self.headers = {'Content-Type': 'application/json'}

    def ask(self, user_id, text):
        # 1. Haqiqiy vaqtni aniqlash
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 2. Xotirani tekshirish
        if user_id not in user_memory:
            user_memory[user_id] = []
        
        # 3. System Prompt (Botning "Dasturi")
        history_context = [
            {
                "role": "user", 
                "parts": [{"text": f"Sen aqlli o'zbek yordamchisan. Bugun: {now}. Suhbatdoshni eslab qolishing shart."}]
            },
            {
                "role": "model", 
                "parts": [{"text": "Tushundim. Men vaqtni bilaman va suhbatimizni eslab qolaman. Qanday yordam bera olaman?"}]
            }
        ]
        
        # Oxirgi 10 ta xabarni qo'shish (Xotira)
        history_context.extend(user_memory[user_id][-10:])
        
        # Yangi so'rov
        history_context.append({"role": "user", "parts": [{"text": text}]})

        try:
            payload = {"contents": history_context}
            res = requests.post(self.url, json=payload, headers=self.headers, timeout=30)
            
            if res.status_code == 200:
                data = res.json()
                ans = data['candidates'][0]['content']['parts'][0]['text']
                
                # Xotirani yangilash (FAQAT muvaffaqiyatli javob bo'lsa)
                user_memory[user_id].append({"role": "user", "parts": [{"text": text}]})
                user_memory[user_id].append({"role": "model", "parts": [{"text": ans}]})
                
                return ans
            elif res.status_code == 400:
                return "❌ API kalit xatosi yoki so'rov formati noto'g'ri. (Check API Key)"
            elif res.status_code == 429:
                return "⏳ So'rovlar juda ko'payib ketdi. Biroz kuting."
            else:
                return f"⚠️ Xatolik kodi: {res.status_code}\nModel hali faollashmagan bo'lishi mumkin."
        except Exception as e:
            return f"❌ Tizimda muammo: {str(e)}"

ai = MasterGemini()

# --- BOT FUNKSIYALARI ---
@bot.message_handler(commands=['start', 'clear'])
def start_cmd(m):
    if m.text == '/clear':
        user_memory[m.from_user.id] = []
        bot.reply_to(m, "🧹 **Suhbat xotirasi tozalandi!** Yangidan gaplashishimiz mumkin.")
    else:
        bot.reply_to(m, "🚀 **Master AI (Gemini Flash) tayyor!**\nMen sizni eslab qola olaman va vaqtni bilaman. Savolingizni bering!")

@bot.message_handler(func=lambda m: True)
def handle_msg(m):
    bot.send_chat_action(m.chat.id, 'typing')
    
    # Gemini AI dan javob olish
    response = ai.ask(m.from_user.id, m.text)
    
    # Telegram limitiga tekshirish
    try:
        if len(response) > 4000:
            for x in range(0, len(response), 4000):
                bot.send_message(m.chat.id, response[x:x+4000])
        else:
            bot.reply_to(m, response)
    except:
        bot.send_message(m.chat.id, "Javob yuborishda xatolik bo'ldi.")

if __name__ == "__main__":
    Thread(target=run_web).start()
    bot.remove_webhook()
    print("Bot muvaffaqiyatli yoqildi!")
    bot.polling(none_stop=True, interval=0)
