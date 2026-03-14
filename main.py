import telebot
import google.generativeai as genai
import requests
import io

# MA'LUMOTLAR - API kalitlarni tekshiring
TELEGRAM_TOKEN = '8780847488:AAE6QJNOXrKiFZdRbKQOb1STnSHC2Lem8to'
GEMINI_API_KEY = 'AIzaSyCSJIyBEwWvDA3h8-FDjsjSxVqoM_FzIZg'

# Sozlamalar
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Rasm yaratish API (Polling AI) - API kalit shart emas
POLLING_IMAGE_API_URL = "https://image.pollinations.ai/prompt/"

@bot.message_handler(func=lambda message: True)
def chat_and_image(message):
    text = message.text.lower().strip()
    
    # 1. Rasm yaratish buyrug'ini tekshirish
    if text.startswith("rasm: ") or text.startswith("/image "):
        # Rasm tavsifini olish
        prompt = text[6:].strip() # "rasm: " yoki "/image " dan keyingi qismini oladi
        
        if not prompt:
            bot.reply_to(message, "Iltimos, rasm tavsifini yozing. Masalan: `rasm: ko'k mashina`")
            return

        bot.reply_to(message, f"Hozir siz uchun rasm yaratayapman: `{prompt}`. Iltimos, kuting...")
        
        try:
            # Polling AI ga so'rov yuborish
            # URL ga prompt qo'shiladi. Masalan: https://image.pollinations.ai/prompt/ko'k mashina
            image_url = POLLING_IMAGE_API_URL + prompt.replace(' ', '%20') # URL uchun probellarni to'g'irlash
            response = requests.get(image_url)
            
            if response.status_code == 200:
                # Rasmni yuborish
                bot.send_photo(message.chat.id, photo=image_url, caption=f"Siz so'ragan rasm: `{prompt}`")
            else:
                bot.reply_to(message, "Kechirasiz, rasm yaratishda xatolik bo'ldi. Keyinroq qayta urining.")
        
        except Exception as e:
            print(f"Rasm yaratishda xatolik: {e}")
            bot.reply_to(message, "Kechirasiz, kutilmagan xatolik yuz berdi.")
    
    # 2. Oddiy matn xabari (Gemini AI bilan)
    else:
        try:
            # Gemini AI dan javob olish
            response = model.generate_content(message.text)
            
            if response.text:
                bot.reply_to(message, response.text)
            else:
                bot.reply_to(message, "Kechirasiz, javob topa olmadim.")
                
        except Exception as e:
            print(f"Matn yaratishda xatolik: {e}")
            bot.reply_to(message, "Matn yaratishda xatolik yuz berdi. Iltimos, API kalitni tekshiring.")

# Boshlash buyrug'i (/start)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Salom! Men Gemini AI botman. Menga xohlagan narsangizni yozishingiz mumkin.\n\nRasm yaratish uchun `rasm: tavsif` deb yozing (masalan: `rasm: ko'k osmon`).")

bot.infinity_polling()
