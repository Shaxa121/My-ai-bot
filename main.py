import telebot, requests, os, time
from threading import Thread
from flask import Flask
from datetime import datetime

# --- KONFIGURATSIYA ---
TOKEN = '8780847488:AAFC_6Hk9CeHNdDkKTmurm-bxAq047K3G0I'
# Avvalgi ishlayotgan Groq API kalitingiz
GROQ_API_KEY = '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'

bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")
app = Flask(__name__)

# Foydalanuvchi xotirasi
user_memory = {}

@app.route('/')
def home(): return "GROQ TURBO WITH MEMORY: ONLINE", 200

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

# --- GROQ LOGIKASI ---
class GroqTurboAI:
    def __init__(self):
        self.url = "https://api.groq.com/openai/v1/chat/completions"
        self.session = requests.Session()
        self.headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

    def ask(self, user_id, text):
        # 1. Haqiqiy vaqtni olish
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 2. Xotirani tekshirish
        if user_id not in user_memory:
            user_memory[user_id] = []
        
        # 3. System Prompt (Botning yo'riqnomasi)
        messages = [
            {
                "role": "system", 
                "content": f"Sen professional o'zbek yordamchisan. Hozirgi vaqt: {now}. Suhbatdoshni eslab qol."
            }
        ]
        
        # 4. Xotiradagi oxirgi 8 ta xabarni qo'shish
        messages.extend(user_memory[user_id][-8:])
        
        # 5. Yangi savolni qo'shish
        messages.append({"role": "user", "content": text})

        try:
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": messages,
                "temperature": 0.6
            }
            res = self.session.post(self.url, json=payload, headers=self.headers, timeout=20)
            
            if res.status_code == 200:
                ans = res.json()['choices'][0]['message']['content'].strip()
                
                # 6. Xotirani yangilash
                user_memory[user_id].append({"role": "user", "content": text})
                user_memory[user_id].append({"role": "assistant", "content": ans})
                
                return ans
            else:
                return f"⚠️ Groq xatosi: {res.status_code}"
        except Exception as e:
            return f"❌ Ulanishda xato: {str(e)}"

ai = GroqTurboAI()

# --- HANDLERS ---
@bot.message_handler(commands=['start', 'clear'])
def start_cmd(m):
    if m.text == '/clear':
        user_memory[m.from_user.id] = []
        bot.reply_to(m, "🧹 **Xotira tozalandi!** Yangidan gaplashishimiz mumkin.")
    else:
        bot.reply_to(m, "🚀 **Groq Turbo AI ishga tushdi!**\n\nMen juda tezman, vaqtni bilaman va sizni eslab qolaman. Savol bering!")

@bot.message_handler(func=lambda m: True)
def handle_msg(m):
    bot.send_chat_action(m.chat.id, 'typing')
    
    # Javobni olish
    response = ai.ask(m.from_user.id, m.text)
    
    try:
        if len(response) > 4000:
            for x in range(0, len(response), 4000):
                bot.send_message(m.chat.id, response[x:x+4000])
        else:
            bot.reply_to(m, response)
    except:
        bot.send_message(m.chat.id, response)

if __name__ == "__main__":
    Thread(target=run_web).start()
    bot.remove_webhook()
    bot.polling(none_stop=True)
