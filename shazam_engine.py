import requests
from config import config

class ShazamEngine:
    def __init__(self):
        self.api_key = config.AUDD_API_KEY
        self.url = "https://api.audd.io/"

    def identify_music(self, file_path):
        """Ovozli fayl orqali musiqani aniqlash"""
        try:
            with open(file_path, 'rb') as f:
                data = {
                    'api_token': self.api_key,
                    'return': 'apple_music,spotify',
                }
                files = {'file': f}
                response = requests.post(self.url, data=data, files=files).json()

            if response.get('status') == 'success' and response.get('result'):
                res = response['result']
                return (
                    f"🎶 **Musiqa topildi!**\n\n"
                    f"🎵 Nom: {res['title']}\n"
                    f"👤 Ijrochi: {res['artist']}\n"
                    f"💿 Albom: {res['album']}"
                )
            return "😔 Musiqani taniy olmadim."
        except Exception as e:
            return f"Muzika modulida xato: {str(e)}"

shazam = ShazamEngine()
