import requests

def get_weather_data(city="Bukhara"):
    try:
        # O'zbek tilida ma'lumot olish
        url = f"https://wttr.in/{city}?format=%c+%t+%C+Namlik:+%h&lang=uz"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return f"🌤 **{city} ob-havosi:**\n\n{response.text}"
        else:
            return "❌ Ob-havo ma'lumotlarini yuklashda xatolik yuz berdi."
    except Exception:
        return "❌ Ob-havo xizmati bilan bog'lanib bo'lmadi."
