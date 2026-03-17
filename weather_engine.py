import requests

def get_weather(city="Bukhara"):
    """
    Berilgan shahar uchun ob-havo ma'lumotlarini qaytaradi.
    wttr.in servisidan foydalaniladi (Tekin va ochiq).
    """
    try:
        # O'zbek tilida ma'lumot olish uchun lang=uz parametrini qo'shamiz
        # format: %c (belgi) %t (harorat) %C (holat) %h (namlik)
        url = f"https://wttr.in/{city}?format=%c+%t+%C+Namlik:+%h&lang=uz"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return f"🌤 **{city} ob-havosi:**\n\n{response.text}"
        else:
            return "❌ Ob-havo ma'lumotlarini yuklashda xatolik yuz berdi."
    except Exception as e:
        return f"❌ Xatolik: Tarmoq bilan bog'lanib bo'lmadi."
