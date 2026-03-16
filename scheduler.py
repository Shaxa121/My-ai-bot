import schedule
import time
from threading import Thread
from weather_engine import weather
from islamic_core import islamic

class MasterScheduler:
    def __init__(self, bot, admin_id):
        self.bot = bot
        self.admin_id = admin_id

    def morning_report(self):
        report = f"☀️ Xayrli tong, Shaxzod!\n\n{weather.get_weather()}\n\n{islamic.get_prayer_times()}"
        self.bot.send_message(self.admin_id, report)

    def run_scheduler(self):
        # Har kuni soat 07:00 da hisobot yuborish
        schedule.every().day.at("07:00").do(self.morning_report)
        
        while True:
            schedule.run_pending()
            time.sleep(60)

    def start(self):
        thread = Thread(target=self.run_scheduler)
        thread.start()

# Bu modul main.py ichida ishga tushiriladi
