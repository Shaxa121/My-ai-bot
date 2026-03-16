import requests
from config import config

class WeatherEngine:
    def __init__(self):
        self.api_key = config.WEATHER_API_KEY
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"

    def get_weather(self, city="Bukhara"):
        try:
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'uz'
            }
            response = requests.get(self.base_url, params=params).json()
            
            if response.get("cod") != 200:
                return "❌ Shahar topilmadi yoki API xatosi."

            temp = response['main']['temp']
            desc = response['weather'][0]['description']
            humidity = response['main']['humidity']
            
            # Aqlli maslahat mantiqi
            advice = "Yengil kiyinib oling."
            if temp < 10: advice = "Issiq kiyining, havo sovuq!"
            elif temp < 20: advice = "Ustingizga nimadir olib oling, salqin."

            return (
                f"🌤 **{city} ob-havosi:**\n"
                f"🌡 Harorat: {temp}°C\n"
                f"📝 Holat: {desc.capitalize()}\n"
                f"💧 Namlik: {humidity}%\n\n"
                f"💡 Maslahat: {advice}"
            )
        except Exception as e:
            return f"Ob-havo tizimida xato: {str(e)}"

weather = WeatherEngine()
