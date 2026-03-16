import requests
from datetime import datetime

class IslamicCore:
    def __init__(self):
        self.api_url = "http://api.aladhan.com/v1/timingsByCity"

    def get_prayer_times(self, city="Bukhara"):
        try:
            params = {
                'city': city,
                'country': 'Uzbekistan',
                'method': 3 # Muslim World League usuli
            }
            data = requests.get(self.api_url, params=params).json()
            timings = data['data']['timings']
            date = data['data']['date']['readable']

            return (
                f"🕌 **{city} Namoz vaqtlari**\n"
                f"📅 Sana: {date}\n\n"
                f"🏙 Bomdod: {timings['Fajr']}\n"
                f"☀️ Quyosh: {timings['Sunrise']}\n"
                f"🌤 Peshin: {timings['Dhuhr']}\n"
                f"🌥 Asr: {timings['Asr']}\n"
                f"🌇 Shom: {timings['Maghrib']}\n"
                f"🌌 Xufton: {timings['Isha']}"
            )
        except Exception as e:
            return "Namoz vaqtlarini olishda xatolik yuz berdi."

islamic = IslamicCore()
