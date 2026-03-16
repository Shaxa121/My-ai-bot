import telebot
import requests
import os
import time
import threading
import base64
import logging
import json
from flask import Flask
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ==========================================
# 1. PROFESSIONAL LOGGING & SETUP
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("bot_log.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# API KALITLAR
TOKEN = '8780847488:AAFC_6Hk9CeHNdDkKTmurm-bxAq047K3G0I'
GROQ_API_KEY = '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'
GEMINI_API_KEY = 'AIzaSyANE76X_SI2TANf2mPj6FQp46QZLYxUIlc'

bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")
app = Flask(__name__)
start_time = datetime.now()

# ==========================================
# 2. XOTIRA VA MA'LUMOTLARNI BOSHQARISH
# ==========================================
class MemoryManager:
    def __init__(self):
        self.db = {}

    def get_user(self, user_id):
        if user_id not in self.db:
            self.db[user_id] = {
                "history": [],
                "reminders": [],
                "stats": {"msgs": 0, "images": 0},
                "settings": {"mode": "creative", "personality": "professional"}
            }
        return self.db[user_id]

    def add_history(self, user_id, role, content):
        user = self.get_user(user_id)
        user["history"].append({"role": role, "content": content})
        if len(user["history"]) > 15:  # Oxirgi 15 ta xabarni saqlash
            user["history"].pop(0)

    def clear(self, user_id):
        if user_id in self.db:
            self.db[user_id]["history"] = []

memory = MemoryManager()

# ==========================================
# 3. AQLLI SETTINGLAR (RETRY SYSTEM)
# ==========================================
def create_session():
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

session = create_session()

# ==========================================
# 4. AI MOTORLARI (PRO DARJA)
# ==========================================
class GlobalAI:
    def __init__(self):
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.gemini_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    def ask_groq(self, user_id, text):
        user = memory.get_user(user_id)
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        sys_msg = f"Sen 'Master AI'san. Hozir: {now}. Suhbatdoshni hurmat qil. Uslub: {user['settings']['personality']}."
        messages = [{"role": "system", "content": sys_msg}]
        messages.extend(user["history"])
        messages.append({"role": "user", "content": text})

        try:
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": messages,
                "temperature": 0.8,
                "top_p": 1
            }
            res = session.post(self.groq_url, json=payload, 
                               headers={"Authorization": f"Bearer {GROQ_API_KEY}"}, timeout=25)
            res.raise_for_status()
            ans = res.json()['choices'][0]['message']['content']
            
            memory.add_history(user_id, "user", text)
            memory.add_history(user_id, "assistant", ans)
            user["stats"]["msgs"] += 1
            return ans
        except Exception as e:
            logger.error(f"Groq Error: {e}")
            return "🛑 Tizimda kichik uzilish bo'ldi. Iltimos, qayta yozing."

    def ask_gemini_vision(self, user_id, b64_data, caption, mime="image/jpeg"):
        payload = {
            "contents": [{
                "parts": [
                    {"text": caption or "Ushbu mediani tahlil qiling."},
                    {"inline_data": {"mime_type": mime, "data": base64_data}}
                ]
            }],
            "generationConfig": {"temperature": 0.4, "maxOutputTokens": 1024}
        }
        try:
            res = session.post(self.gemini_url, json=payload, timeout=45)
            res.raise_for_status()
            user = memory.get_user(user_id)
            user["stats"]["images"] += 1
            return res.json()['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            logger.error(f"Gemini Error: {e}")
            return "❌ Tasvirni tahlil qilib bo'lmadi."

ai = GlobalAI()

# ==========================================
# 5. ADMIN VA STATISTIKA
# ==========================================
def get_system_stats():
    uptime = datetime.now() - start_time
    return (f"📊 **Bot Statistikasi:**\n"
            f"⏱ Ish vaqti: {str(uptime).split('.')[0]}\n"
            f"👥 Foydalanuvchilar: {len(memory.db)}\n"
            f"📡 Server: Render Cloud")

# ==========================================
# 6. TELEGRAM EVENT HANDLERS
# ==========================================
@bot.message_handler(commands=['start'])
def cmd_start(m):
    welcome = (f"🌟 **Assalomu alaykum, {m.from_user.first_name}!**\n\n"
               "Men eng mukammal gibrid AI tizimiman.\n\n"
               "🛠 **Imkoniyatlar:**\n"
               "1️⃣ Tezkor chat (Groq Llama 3.3)\n"
               "2️⃣ Rasm va Fayl tahlili (Gemini)\n"
               "3️⃣ Aqlli eslatmalar (`/remind`)\n"
               "4️⃣ Shaxsiy statistika (`/stats`)\n\n"
               "💡 _Savolingizni yuboring yoki rasm yuklang!_")
    bot.send_message(m.chat.id, welcome)

@bot.message_handler(commands=['stats'])
def cmd_stats(m):
    user = memory.get_user(m.from_user.id)
    text = (f"👤 **Sizning hisobingiz:**\n"
            f"💬 Xabarlar: {user['stats']['msgs']}\n"
            f"🖼 Rasmlar: {user['stats']['images']}\n\n"
            f"{get_system_stats()}")
    bot.reply_to(m, text)

@bot.message_handler(commands=['clear'])
def cmd_clear(m):
    memory.clear(m.from_user.id)
    bot.reply_to(m, "🧹 **Suhbat tarixi tozalandi.**")

@bot.message_handler(commands=['remind'])
def cmd_remind(m):
    try:
        parts = m.text.split(maxsplit=2)
        minutes = int(parts[1])
        text = parts[2]
        target_time = datetime.now() + timedelta(minutes=minutes)
        
        scheduler.add_job(
            lambda: bot.send_message(m.chat.id, f"⏰ **ESLATMA!**\n\n🔔 {text}"),
            'date', run_date=target_time
        )
        bot.reply_to(m, f"✅ Rejalashtirildi: {target_time.strftime('%H:%M')}")
    except:
        bot.reply_to(m, "❌ Format: `/remind 10 Non olish`")

# MEDIA HANDLER
@bot.message_handler(content_types=['photo', 'document', 'audio'])
def handle_media(m):
    wait = bot.reply_to(m, "🔄 **Media qayta ishlanmoqda...**")
    try:
        if m.content_type == 'photo':
            fid = m.photo[-1].file_id
            mtype = "image/jpeg"
        elif m.content_type == 'document':
            fid = m.document.file_id
            mtype = m.document.mime_type
        else:
            return bot.edit_message_text("❌ Bu formatni qo'llab-quvvatlamayman.", m.chat.id, wait.message_id)

        finfo = bot.get_file(fid)
        data = bot.download_file(finfo.file_path)
        b64 = base64.b64encode(data).decode('utf-8')
        
        caption = m.caption or "Tahlil ber."
        res = ai.ask_gemini_vision(m.from_user.id, b64, caption, mtype)
        
        # Javob uzun bo'lsa bo'lib yuborish
        if len(res) > 4000:
            bot.delete_message(m.chat.id, wait.message_id)
            for i in range(0, len(res), 4000):
                bot.send_message(m.chat.id, res[i:i+4000])
        else:
            bot.edit_message_text(f"📝 **Tahlil:**\n\n{res}", m.chat.id, wait.message_id)
    except Exception as e:
        bot.edit_message_text(f"⚠️ Xato: {str(e)}", m.chat.id, wait.message_id)

# TEXT HANDLER
@bot.message_handler(func=lambda m: True)
def handle_all_text(m):
    bot.send_chat_action(m.chat.id, 'typing')
    response = ai.ask_groq(m.from_user.id, m.text)
    
    try:
        bot.reply_to(m, response)
    except:
        bot.send_message(m.chat.id, response)

# ==========================================
# 7. SERVER & KEEP-ALIVE
# ==========================================
@app.route('/')
def index():
    return {"status": "online", "users": len(memory.db), "uptime": str(datetime.now()-start_time)}, 200

def run_server():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

scheduler = BackgroundScheduler()
scheduler.start()

if __name__ == "__main__":
    logger.info("Ultimate AI Bot starting...")
    threading.Thread(target=run_server, daemon=True).start()
    
    # Render'da bot o'chib qolmasligi uchun cheksiz sikl
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
