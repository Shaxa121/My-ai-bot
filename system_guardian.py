import psutil
import platform
import os
import traceback
from datetime import datetime

class SystemGuardian:
    def __init__(self):
        self.start_time = datetime.now()

    def get_system_health(self):
        """Server holatini tekshirish (CPU, RAM)"""
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        uptime = datetime.now() - self.start_time
        
        return (
            f"🛡 **Guardian Diagnostikasi:**\n"
            f"⏱ **Uptime:** {str(uptime).split('.')[0]}\n"
            f"📊 **CPU:** {cpu}%\n"
            f"💾 **RAM:** {ram}%\n"
            f"📍 **Platforma:** {platform.system()}"
        )

    def report_error(self, error_traceback):
        """Xatoni rentgen qilish"""
        return f"🚨 **XATOLIK ANIQLANDI!**\n\n`{error_traceback}`"

guardian = SystemGuardian()
