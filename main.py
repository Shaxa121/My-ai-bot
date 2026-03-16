import telebot, requests, os, time, threading, base64
from flask import Flask
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

# --- KONFIGURATSIYA ---
TOKEN = '8780847488:AAFC_6Hk9CeHNdDkKTmurm-bxAq047K3G0I'
GROQ_API_KEY = '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'
GEMINI_API_KEY = 'AIzaSyBxV4e1njS4O9jvegWFs7mVXEAxz039ReY' # Oxirgi bergan kalitingiz

bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")
app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()

user_memory = {}

@app.route('/')
def home(): return "HYBRID AI: GROQ + GEMINI ONLINE", 200

# --- ESLATMA FUNKSIYASI ---
def send_reminder(chat_id, text):
    bot.send_message(chat_id, f"⏰ **ESLATMA:**\n\n🔔 {text}")

# --- AI KLASSI ---
class HybridAI:
    def __init__(self):
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    # Matn uchun Groq
    def ask_text(self, user_id, text):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if user_id not in user_memory: user_memory[user_id] = []
        messages = [{"role": "system", "content": f"Sen aqlli yordamchisan. Hozir: {now}. O'zbekcha gaplash."}]
        messages.extend(user_memory[user_id][-6:])
        messages.append({"role": "user", "content": text})
        try:
            res = requests.post(self.groq_url, json={"model": "llama-3.3-70b-versatile", "messages": messages}, 
                                headers={"Authorization": f"Bearer {GROQ_API_KEY}"}, timeout=20)
            ans = res.json()['choices'][0]['message']['content'].strip()
            user_memory[user_id].append({"role": "user", "content": text})
            user_memory[user_id].append({"role": "assistant", "content": ans})
            return ans
        except: return "❌ Groq matnli javobda xatolik."

    # Rasm uchun Gemini
    def analyze_image(self, base64_image, prompt_text):
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt_text},
                    {"inline_data": {"mime_type": "image/jpeg", "data": base64_image}}
                ]
            }]
        }
        try:
            res = requests.post(self.gemini_url, json=payload, headers={'Content-Type': 'application/json'}, timeout=30)
            if res.status_code == 200:
                return res.json()['candidates'][0]['content']['parts'][0]['text']
            else:
                return f"⚠️ Gemini xatosi: {res.status_code}"
        except: return "❌ Gemini rasm tahlilida xatolik."

ai = HybridAI()

# --- HANDLERS ---
@bot.message_handler(commands=['start', 'clear'])
def start_cmd(m):
    if m.text == '/clear':
        user_memory[m.from_user.id] = []
        bot.reply_to(m, "🧹 Xotira tozalandi.")
    else:
        bot.reply_to(m, "🚀 **Gibrid AI bot tayyor!**\n\n- Matnlar: **Groq** (Tezkor)\n- Rasmlar: **Gemini** (Aniq)\n- Eslatma: `/remind minut matn`")

@bot.message_handler(commands=['remind'])
def set_reminder(m):
    try:
        parts = m.text.split(' ', 2)
        minutes, text = int(parts[1]), parts[2]
        run_time = datetime.now() + timedelta(minutes=minutes)
        scheduler.add_job(send_reminder, 'date', run_date=run_time, args=[m.chat.id, text])
        bot.reply_to(m, f"✅ Eslatma {minutes} minutga qo'yildi.")
    except: bot.reply_to(m, "❌ Format: `/remind 5 dars`")

@bot.message_handler(content_types=['photo'])
def handle_photo(m):
    wait_msg = bot.reply_to(m, "📸 **Gemini rasmni o'rganmoqda...**")
    try:
        file_info = bot.get_file(m.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        base64_img = base64.b64encode(downloaded_file).decode('utf-8')
        
        prompt = m.caption if m.caption else "Bu rasmda nima bor? O'zbekcha tushuntir."
        analysis = ai.analyze_image(base64_img, prompt)
        bot.edit_message_text(f"🖼 **Rasm tahlili (Gemini):**\n\n{analysis}", m.chat.id, wait_msg.message_id)
    except Exception as e:
        bot.edit_message_text("❌ Rasmni yuklashda xato.", m.chat.id, wait_msg.message_id)

@bot.message_handler(func=lambda m: True)
def handle_msg(m):
    bot.send_chat_action(m.chat.id, 'typing')
    response = ai.ask_text(m.from_user.id, m.text)
    bot.reply_to(m, response)

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000))), daemon=True).start()
    bot.polling(none_stop=True)
