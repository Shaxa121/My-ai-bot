from config import config
from system_guardian import guardian

class AdminPanel:
    def __init__(self):
        self.admin_id = config.ADMIN_ID

    def is_admin(self, user_id):
        return str(user_id) == str(self.admin_id)

    def get_stats(self):
        """Bot statistikasi (Hozircha Guardian ma'lumotlari bilan)"""
        health = guardian.get_system_health()
        return f"📊 **Admin Panel - Statistika**\n\n{health}"

admin_p = AdminPanel()
