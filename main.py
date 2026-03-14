import telebot
import requests
import os
import time
from flask import Flask
from threading import Thread

# --- SOZLAMALAR ---
TELEGRAM_TOKEN = '8728653741:AAEv9k3NdQfnaFtxfMY8pxrE1l3kEQC_zlk'
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# --- RENDER SERVER (404 VA TIMEOUT XATOLARI UCHUN) ---
app = Flask(__name__)

@app.route('/')
def health():
    return "Bot is Live and Active!", 200

def run():
    # Render portni avtomatik beradi
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- AQLLI AI FUNKSIYASI (Blackbox GPT-4o) ---
def get_ai_answer(text):
    try:
        url = "https://api.blackbox.ai/api/chat"
        payload = {
            "messages": [
                {"role": "user", "content": text + " (iltimos, faqat o'zbek tilida javob ber)"}
            ],
            "model": "deepseek-v3",
            "max_tokens": 1024
        }
        headers = {"Content-Type": "application/json"}
        res = requests.post(url, json=payload, timeout=20)
        
        # Ortiqcha texnik belgilarni tozalash
        full_text = res.text.split('$@$')[0].strip()
        return full_text if full_text else "Savolingizni tushunmadim, qaytadan yozing."
    except Exception as e:
        print(f"AI Error: {e}")
        return "Hozircha tizimda yuklama bor. Birozdan keyin urinib ko'ring!"

# --- BOT BUYRUQLARI ---
@bot.message_handler(commands=['start'])
def welcome(message):
    welcome_msg = (
        f"🌟 *Assalomu alaykum, {message.from_user.first_name}!*\n\n"
        "Men yangi va aqlli AI yordamchingizman. 🚀\n"
        "Menga istalgan savolingizni bering yoki rasm chizdiring.\n\n"
        "🖼 *Rasm uchun:* `rasm: [tavsif]` deb yozing."
    )
    bot.send_message(message.chat.id, welcome_msg, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    msg = message.text
    chat_id = message.chat.id
    
    if msg.lower().startswith("rasm:"):
        prompt = msg[5:].strip()
        bot.reply_to(message, "🎨 *Rasm tayyorlanmoqda, kuting...*", parse_mode="Markdown")
        image_url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}?width=1024&height=1024&nologo=true"
        bot.send_photo(chat_id, photo=image_url, caption=f"🖼 *Natija:* {prompt}", parse_mode="Markdown")
    else:
        bot.send_chat_action(chat_id, 'typing')
        answer = get_ai_answer(msg)
        bot.reply_to(message, answer)

# --- ISHGA TUSHIRISH ---
if __name__ == "__main__":
    # Serverni orqa fonda yoqish
    Thread(target=run).start()
    
    # Eski ulanishlarni tozalash
    bot.remove_webhook()
    time.sleep(2)
    
    print("Bot muvaffaqiyatli ishga tushdi!")
    # Stabil polling rejimi
    bot.polling(none_stop=True, interval=0, timeout=20)
