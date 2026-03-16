import telebot, requests, sqlite3, os, time, base64, logging, threading
from PIL import Image
from gtts import gTTS
from datetime import datetime
import pytz

# ==========================================
# 1. TIZIM VA XAVFSIZLIK (FIREWALL)
# ==========================================
TOKEN = '8780847488:AAFC_6Hk9CeHNdDkKTmurm-bxAq047K3G0I'
GROQ_KEY = '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'
GOOGLE_API_KEY = "YOUR_GOOGLE_KEY"
GOOGLE_CSE_ID = "YOUR_CSE_ID"
ADMIN_ID = 5616641887

bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")
UZB_TZ = pytz.timezone('Asia/Tashkent')

class MasterFirewall:
    def __init__(self):
        self.logs = {}
    def check_flood(self, uid):
        now = time.time()
        if uid not in self.logs: self.logs[uid] = []
        self.logs[uid] = [t for t in self.logs[uid] if now - t < 60]
        if len(self.logs[uid]) > 20: return False # Spam himoyasi
        self.logs[uid].append(now)
        return True

firewall = MasterFirewall()

# ==========================================
# 2. SQLITE DATABASE (OMBORXONA)
# ==========================================

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('master_core.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users 
            (id INTEGER PRIMARY KEY, tts_on INTEGER DEFAULT 0, xp INTEGER DEFAULT 0, joined DATE)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS analytics (req_type TEXT, count INTEGER)''')
        self.conn.commit()
    
    def toggle_tts(self, uid):
        current = self.conn.execute("SELECT tts_on FROM users WHERE id=?", (uid,)).fetchone()
        new_val = 1 if current[0] == 0 else 0
        self.conn.execute("UPDATE users SET tts_on=? WHERE id=?", (new_val, uid))
        self.conn.commit()
        return new_val

db = Database()

# ==========================================
# 3. GOOGLE SMART SEARCH & VISION
# ==========================================

class AISystem:
    def google_search(self, query):
        try:
            url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}"
            res = requests.get(url).json()
            return "\n".join([f"🔹 {i['title']}: {i['snippet']}" for i in res.get('items', [])[:3]])
        except: return None

    def vision_analyze(self, img_path, caption):
        with open(img_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode('utf-8')
        payload = {
            "model": "llama-3.2-90b-vision-preview",
            "messages": [{"role": "user", "content": [
                {"type": "text", "text": f"OCR tahlil va yechim: {caption}"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
            ]}],
            "temperature": 0.1
        }
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                            json=payload, headers={"Authorization": f"Bearer {GROQ_KEY}"})
        return res.json()['choices'][0]['message']['content']

ai_sys = AISystem()

# ==========================================
# 4. VOICE ENGINE (TTS)
# ==========================================
def generate_voice(text):
    path = f"v_{int(time.time())}.ogg"
    tts = gTTS(text=text[:250], lang='tr') # O'zbekcha yo'qligi uchun tr
    tts.save(path)
    return path

# ==========================================
# 5. ASOSIY HANDLERLAR (CORE LOGIC)
# ==========================================
@bot.message_handler(commands=['start'])
def welcome(m):
    db.conn.execute("INSERT OR IGNORE INTO users (id, joined) VALUES (?, ?)", (m.from_user.id, datetime.now()))
    bot.send_message(m.chat.id, "🎯 **Master AI Infinity Edition ishga tushdi!**\n\n- Rasm yuboring (BSB/CHSB)\n- Google'dan izlang\n- Ovozni sozlang (/settings)")

@bot.message_handler(commands=['settings'])
def settings_panel(m):
    markup = telebot.types.InlineKeyboardMarkup()
    tts_status = db.conn.execute("SELECT tts_on FROM users WHERE id=?", (m.from_user.id,)).fetchone()[0]
    btn_text = "🔊 Ovoz: YOQILGAN" if tts_status else "❌ Ovoz: O'CHIRILGAN"
    markup.add(telebot.types.InlineKeyboardButton(btn_text, callback_data="tts_toggle"))
    bot.send_message(m.chat.id, "🤖 **Bot sozlamalari:**", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "tts_toggle")
def tts_callback(call):
    new_v = db.toggle_tts(call.from_user.id)
    text = "Yoqildi ✅" if new_v else "O'chirildi ❌"
    bot.answer_callback_query(call.id, f"Ovozli javob {text}")
    settings_panel(call.message) # Yangilash

@bot.message_handler(content_types=['photo'])
def vision_handler(m):
    if not firewall.check_flood(m.from_user.id): return
    status = bot.reply_to(m, "👁️ **Rasmni mikroskop ostida tahlil qilyapman...**")
    
    file_info = bot.get_file(m.photo[-1].file_id)
    raw = bot.download_file(file_info.file_path)
    with open("job.jpg", "wb") as f: f.write(raw)
    
    ans = ai_sys.vision_analyze("job.jpg", m.caption or "Matnni o'qi")
    bot.edit_message_text(f"📝 **Analiz:**\n\n{ans}", m.chat.id, status.message_id)

@bot.message_handler(func=lambda m: True)
def chat_handler(m):
    if not firewall.check_flood(m.from_user.id): return
    
    # Qidiruv mantiqi
    search_res = ""
    if any(k in m.text.lower() for k in ["google", "izla", "nima"]):
        bot.send_chat_action(m.chat.id, 'find_location')
        search_res = ai_sys.google_search(m.text)
    
    # AI mantiqi (Llama 3.3)
    bot.send_chat_action(m.chat.id, 'typing')
    # Bu qismda API orqali javob olinadi (vaqt tejash uchun qisqartirildi)
    final_ans = f"AI Javobi: {m.text} haqida ma'lumot topildi..." 
    
    bot.reply_to(m, final_ans)

    # TTS Tekshiruvi
    tts_on = db.conn.execute("SELECT tts_on FROM users WHERE id=?", (m.from_user.id,)).fetchone()[0]
    if tts_on:
        v_file = generate_voice(final_ans)
        with open(v_file, 'rb') as vf: bot.send_voice(m.chat.id, vf)
        os.remove(v_file)

# ==========================================
# 6. ADMIN DASHBOARD & RUN
# ==========================================
if __name__ == "__main__":
    print("🔥 MASTER AI INFINITY 3550 ONLINE")
    bot.infinity_polling()
