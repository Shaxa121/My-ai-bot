import telebot
import google.generativeai as genai
import requests
import os
from telebot import types

# --- SOZLAMALAR ---
TELEGRAM_TOKEN = '8780847488:AAE6QJNOXrKiFZdRbKQOb1STnSHC2Lem8to'
GEMINI_API_KEY = 'AIzaSyBxrvfyheIXzhNTHkfbXRRw7pTl_iwfwBQ'

# Gemini AI ni sozlash (Eng ishonchli usul)
try:
    genai.configure(api_key=GEMINI_API_KEY)
    # Modelni yuklash
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("Gemini muvaffaqiyatli sozlandi!")
except Exception as e:
    print(f"Gemini sozlashda xatolik: {e}")

# Botni ishga tushirish
bot = telebot.TeleBot(TELEGRAM_TOKEN, parse_mode="Markdown")

# --- KLAVIATURA (MENYU) ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("🤖 AI bilan gaplashish")
    item2 = types.KeyboardButton("🎨 Rasm yaratish")
    item3 = types.KeyboardButton("ℹ️ Yordam")
    markup.add(item1, item2)
    markup.add(item3)
    return markup

# --- BUYRUQLAR ---
@bot.message_handler(commands=['start'])
def welcome(message):
    welcome_text = (
        f"👋 *Assalomu alaykum, {message.from_user.first_name}!* \n\n"
        "Men yangilangan, kuchliroq AI botman! 🚀\n"
        "Savol bo'lsa yozing yoki rasm chizdiring."
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu())

# --- ASOSIY ISHLOVCHI ---
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    msg = message.text
    chat_id = message.chat.id

    # Rasm yaratish (rasm: so'zi bo'lsa)
    if msg.lower().startswith("rasm:"):
        prompt = msg[5:].strip()
        if not prompt:
            bot.reply_to(message, "⚠️ Iltimos, rasm tavsifini kiriting!")
            return

        sent_msg = bot.reply_to(message, "🎨 *Rasm tayyorlanmoqda, kuting...*")
        try:
            image_url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}?width=1024&height=1024&nologo=true"
            bot.send_photo(chat_id, photo=image_url, caption=f"🖼 *Natija:* {prompt}")
            bot.delete_message(chat_id, sent_msg.message_id)
        except Exception as e:
            bot.edit_message_text("❌ Rasm yaratishda xatolik yuz berdi.", chat_id, sent_msg.message_id)

    # Matn yaratish (AI bilan)
    else:
        bot.send_chat_action(chat_id, 'typing')
        try:
            # Diqqat: Bu qatorda xato ehtimolini kamaytirish uchun to'g'ridan-to'g'ri chaqiramiz
            response = model.generate_content(msg)
            
            if response and response.text:
                bot.reply_to(message, response.text)
            else:
                bot.reply_to(message, "🧐 Gemini javob qaytarmadi. API kalitda hali ham cheklov bo'lishi mumkin.")
        except Exception as e:
            # Xatolikni aniq ko'rish uchun foydalanuvchiga yuboramiz
            bot.reply_to(message, f"❌ Xatolik turi: {type(e).__name__}\nIltimos, qayta urinib ko'ring yoki biroz kuting.")

# Botni to'xtovsiz ishlatish
bot.infinity_polling()
