import telebot
import requests
import os
import time
from flask import Flask
from threading import Thread

# --- SOZLAMALAR ---
TELEGRAM_TOKEN = '8780847488:AAE6QJNOXrKiFZdRbKQOb1STnSHC2Lem8to'
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# --- RENDER UCHUN SERVER (SERVERNI ALDASH) ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is Active!", 200

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- AQLLI AI FUNKSIYASI (GPT-4 DARAJASIDA) ---
def get_ai_response(text):
    try:
        url = "https://api.blackbox.ai/api/chat"
        payload = {
            "messages": [
                {"role": "user", "content": text}
            ],
            "model": "deepseek-v3", # Eng yangi va aqlli model
            "max_tokens": "1024"
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, timeout=15)
        
        if response.status_code == 200:
            # Ba'zan Blackbox javobni biroz boshqacha formatda qaytaradi
            return response.text.replace("$@$v=undefined-rv1$@$", "").strip()
        else:
            return "Hozircha tizim band. Birozdan keyin urinib ko'ring."
    except Exception as e:
        print(f"Xatolik: {e}")
        return "Uzr, savolingizni tushunishda biroz qiynaldim. Qayta yozing-chi?"

# --- BOT BUYRUQLARI ---
@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = (
        f"👋 Salom, {message.from_user.first_name}!\n\n"
        "Men yangilangan, haqiqiy **Aqlli AI** botman. 🚀\n"
        "Menga istalgan savolingizni bering yoki rasm chizdiring!\n\n"
        "🎨 *Rasm uchun:* `rasm: [tavsif]`"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    msg = message.text
    chat_id = message.chat.id

    if msg.lower().startswith("rasm:"):
        prompt = msg[5:].strip()
        bot.reply_to(message, "🎨 *Rasm tayyorlanmoqda, kuting...*", parse_mode="Markdown")
        image_url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}?width=1024&height=1024"
        bot.send_photo(chat_id, photo=image_url, caption=f"🖼 *Natija:* {prompt}", parse_mode="Markdown")
    else:
        bot.send_chat_action(chat_id, 'typing')
        ai_reply = get_ai_response(msg)
        bot.reply_to(message, ai_reply)

# --- ISHGA TUSHIRISH (CONFLICT 409 NI OLDINI OLISH) ---
if __name__ == "__main__":
    # Serverni yoqish
    Thread(target=run).start()
    
    # Conflict 409 bo'lmasligi uchun Telegramga "men kelyapman" deymiz
    bot.remove_webhook()
    time.sleep(1)
    
    print("Bot polling boshlandi...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
