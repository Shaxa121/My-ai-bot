import telebot
import google.generativeai as genai

# MA'LUMOTLAR
TELEGRAM_TOKEN = '8780847488:AAE6QJNOXrKiFZdRbKQOb1STnSHC2Lem8to'
GEMINI_API_KEY = 'AIzaSyCSJIyBEwWvDA3h8-FDjsjSxVqoM_FzIZg'

# Sozlamalar
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(func=lambda message: True)
def chat(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception:
        bot.reply_to(message, "Xatolik bo'ldi, qaytadan yozing.")

bot.infinity_polling()
