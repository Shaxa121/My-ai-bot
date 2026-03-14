import telebot
import requests
import g4f # Bu kutubxona Gemini ishlamasa yordamga keladi
from telebot import types

# --- SOZLAMALAR ---
TELEGRAM_TOKEN = '8780847488:AAE6QJNOXrKiFZdRbKQOb1STnSHC2Lem8to'
bot = telebot.TeleBot(TELEGRAM_TOKEN, parse_mode="Markdown")

def get_ai_response(user_text):
    try:
        # Tekin va kalit so'ramaydigan modeldan foydalanamiz
        response = g4f.ChatCompletion.create(
            model=g4f.models.gpt_4,
            messages=[{"role": "user", "content": user_text}],
        )
        return response
    except Exception as e:
        return "Hozircha javob bera olmayman, birozdan keyin urinib ko'ring."

# --- KLAVIATURA ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🤖 AI bilan gaplashish"), types.KeyboardButton("🎨 Rasm yaratish"))
    return markup

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "Salom! Men har doim ishlaydigan AI botman. Savolingizni yozing!", reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    msg = message.text
    if msg.lower().startswith("rasm:"):
        prompt = msg[5:].strip()
        bot.reply_to(message, "🎨 Rasm tayyorlanyapti...")
        image_url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}"
        bot.send_photo(message.chat.id, photo=image_url)
    else:
        bot.send_chat_action(message.chat.id, 'typing')
        ai_reply = get_ai_response(msg)
        bot.reply_to(message, ai_reply)

bot.infinity_polling()
