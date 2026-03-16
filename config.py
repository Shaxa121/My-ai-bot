import os

class Config:
    """
    Master AI Infinity: Beast Edition - Konfiguratsiya markazi.
    """
    # 🤖 Telegram Bot Token
    BOT_TOKEN = "7854228914:AAH_..." # Siz bergan token shu yerda
    
    # 🧠 AI Cloud Keys (Brain & Vision)
    GROQ_API_KEY = "gsk_yV8N..." # Siz bergan Groq API
    GEMINI_API_KEY = "AIzaSy..." # Siz bergan Gemini API
    
    # 🌦 Multimedia & Utility APIs
    WEATHER_API_KEY = "6b7..." # OpenWeatherMap kaliti
    AUDD_API_KEY = "3a8..." # Musiqa tanish (Shazam) kaliti
    
    # 👤 Admin Ma'lumotlari
    ADMIN_ID = 5612345678 # Shaxzodning ID raqami
    
    # 📂 Tizim sozlamalari
    DB_NAME = "master_infinity_v4.db"
    PORT = int(os.environ.get('PORT', 8080))
    
    # 🛡 Xavfsizlik limitlari
    MAX_VIDEO_SIZE = 50 * 1024 * 1024 # 50MB (Telegram limit)
    MAX_TEXT_CHUNK = 4000 # Xabar bo'laklash uzunligi

# Obyekt yaratish
config = Config()
