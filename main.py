import telebot
import google.generativeai as genai
import requests
from telebot import types

# --- SOZLAMALAR ---
TELEGRAM_TOKEN = '8780847488:AAE6QJNOXrKiFZdRbKQOb1STnSHC2Lem8to'
GEMINI_API_KEY = 'AIzaSyAsSbVpvsRpOcryHkuCkGCW4qy_MEhFHLg'

# Gemini AI ni sozlash
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

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
        f"👋 *Assalomu alaykum, {message.from_user.first_name}!*\n\n"
        "Men sening shaxsiy sun'iy intellekt yordamchingman.\n"
        "Matn yozsangiz - javob beraman, 'rasm:' deb yozsangiz - chizib beraman!"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu())

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = (
        "❓ *Qanday foydalanish kerak?*\n\n"
        "1️⃣ **Savol bering:** Shunchaki xabar yuboring.\n"
        "2️⃣ **Rasm yarating:** `rasm: [tavsif]` shaklida yozing.\n"
        "   _Misol: rasm: kosmosdagi o'zbek palovi_\n"
        "3️⃣ **Menyu:** Pastdagi tugmalardan foydalaning."
    )
    bot.send_message(message.chat.id, help_text)

# --- ASOSIY ISHLOVCHI ---
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    msg = message.text
    chat_id = message.chat.id

    # Tugmalarni tekshirish
    if msg == "🤖 AI bilan gaplashish":
        bot.send_message(chat_id, "Qanday savolingiz bor? Bemalol so'rang!")
        return
    elif msg == "🎨 Rasm yaratish":
        bot.send_message(chat_id, "Rasm yaratish uchun: `rasm: [tavsif]` deb yozing.")
        return
    elif msg == "ℹ️ Yordam":
        help_command(message)
        return

    # RASM YARATISH (rasm: so'zi bo'lsa)
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

    # MATN YARATISH (AI bilan)
    else:
        # Bot "yozmoqda..." statusini ko'rsatadi
        bot.send_chat_action(chat_id, 'typing')
        
        try:
            response = model.generate_content(msg)
            if response.text:
                # Agar javob juda uzun bo'lsa, qismlarga bo'ladi
                if len(response.text) > 4096:
                    for x in range(0, len(response.text), 4096):
                        bot.send_message(chat_id, response.text[x:x+4096])
                else:
                    bot.reply_to(message, response.text)
            else:
                bot.reply_to(message, "🧐 Javob topa olmadim, savolni boshqacharoq bering.")
        except Exception as e:
            bot.reply_to(message, "🛠 *Hozircha javob bera olmayman. API kalitni tekshiring yoki keyinroq urining.*")

# Botni to'xtovsiz ishlatish
print("Bot ishga tushdi...")
bot.infinity_polling()
