import telebot, requests, os, time, threading, base64
from flask import Flask
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

# --- KONFIGURATSIYA ---
TOKEN = '8780847488:AAFC_6Hk9CeHNdDkKTmurm-bxAq047K3G0I'
GROQ_API_KEY = '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'

bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")
app = Flask(__name__)

# Eslatmalar uchun rejalashtiruvchi
scheduler = BackgroundScheduler()
scheduler.start()

# Foydalanuvchi xotirasi
user_memory = {}

@app.route('/')
def home(): return "AI ASSISTANT + VISION + REMINDER: ONLINE", 200

# --- ESLATMA FUNKSIYASI ---
def send_reminder(chat_id, text):
    bot.send_message(chat_id, f"⏰ **DIQQAT! ESLATMA:**\n\n🔔 _{text}_")

# --- GROQ AI LOGIKASI ---
class GroqAI:
    def __init__(self):
        self.url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}

    # 1. Oddiy matnli chat funksiyasi
    def ask(self, user_id, text):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if user_id not in user_memory: user_memory[user_id] = []
        
        messages = [{"role": "system", "content": f"Sen aqlli yordamchisan. Hozir: {now}. O'zbekcha gaplash."}]
        messages.extend(user_memory[user_id][-6:])
        messages.append({"role": "user", "content": text})

        try:
            res = requests.post(self.url, json={"model": "llama-3.3-70b-versatile", "messages": messages}, headers=self.headers, timeout=20)
            ans = res.json()['choices'][0]['message']['content'].strip()
            user_memory[user_id].append({"role": "user", "content": text})
            user_memory[user_id].append({"role": "assistant", "content": ans})
            return ans
        except: return "❌ AI hozir matnga javob bera olmaydi."

    # 2. YANGI: Rasm tahlil qilish funksiyasi
    def analyze_image(self, base64_image, prompt_text):
        payload = {
            "model": "llama-3.2-11b-vision-preview", # Groq Vision modeli
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            "temperature": 0.5
        }
        try:
            res = requests.post(self.url, json=payload, headers=self.headers, timeout=30)
            if res.status_code == 200:
                return res.json()['choices'][0]['message']['content'].strip()
            else:
                return f"⚠️ API xatosi: {res.status_code}"
        except Exception as e:
            return f"❌ Rasmni tahlil qilishda xatolik yuz berdi."

ai = GroqAI()

# --- BOT HANDLERS ---
@bot.message_handler(commands=['start', 'clear'])
def start_cmd(m):
    if m.text == '/clear':
        user_memory[m.from_user.id] = []
        bot.reply_to(m, "🧹 Xotira tozalandi.")
    else:
        bot.reply_to(m, "👋 **Salom! Men Super AI Yordamchiman.**\n\n"
                        "💬 Matn yozishingiz, eslatma qo'yishingiz (`/remind 5 dars qilish`) "
                        "yoki **menga rasm yuborishingiz** mumkin, men uni tahlil qilib beraman!")

@bot.message_handler(commands=['remind'])
def set_reminder(m):
    try:
        parts = m.text.split(' ', 2)
        minutes = int(parts[1])
        reminder_text = parts[2]
        run_time = datetime.now() + timedelta(minutes=minutes)
        scheduler.add_job(send_reminder, 'date', run_date=run_time, args=[m.chat.id, reminder_text])
        bot.reply_to(m, f"✅ **Eslatma saqlandi!**\n⏳ {minutes} minutdan keyin xabar yuboraman.")
    except:
        bot.reply_to(m, "❌ Xato! Format: `/remind minut matn`")

# YANGI: Rasmlarni qabul qiluvchi qism
@bot.message_handler(content_types=['photo'])
def handle_photo(m):
    wait_msg = bot.reply_to(m, "👁 **Rasmni o'rganyapman, iltimos kuting...**")
    try:
        # 1. Rasmni Telegram serveridan yuklab olish (eng yuqori sifatdagisini: -1)
        file_info = bot.get_file(m.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # 2. Rasmni Base64 formatiga o'girish (API ga tushunarli bo'lishi uchun)
        base64_img = base64.b64encode(downloaded_file).decode('utf-8')
        
        # 3. Agar foydalanuvchi rasm ostiga yozuv qoldirgan bo'lsa, o'shani so'raymiz
        prompt = m.caption if m.caption else "Bu rasmda nima tasvirlanganini o'zbek tilida batafsil tushuntirib ber."
        
        # 4. Groq Vision orqali tahlil qilish
        analysis = ai.analyze_image(base64_img, prompt)
        
        bot.edit_message_text(f"🖼 **Rasm tahlili:**\n\n{analysis}", m.chat.id, wait_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Kechirasiz, rasmni ochishda muammo bo'ldi: {str(e)}", m.chat.id, wait_msg.message_id)

@bot.message_handler(func=lambda m: True)
def handle_msg(m):
    bot.send_chat_action(m.chat.id, 'typing')
    response = ai.ask(m.from_user.id, m.text)
    bot.reply_to(m, response)

# --- ISHGA TUSHIRISH ---
if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000))), daemon=True).start()
    bot.polling(none_stop=True)
