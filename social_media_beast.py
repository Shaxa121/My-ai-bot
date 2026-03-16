import yt_dlp
import os
import time
import logging

logger = logging.getLogger("MediaBeast")

class MediaBeast:
    def __init__(self):
        self.download_path = "downloads"
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)

    def download_video(self, url):
        """
        Instagram, TikTok va YouTube uchun universal yuklovchi mantiq.
        """
        # Har bir yuklash uchun alohida nom berish (to'qnashuv bo'lmasligi uchun)
        timestamp = int(time.time())
        out_template = f"{self.download_path}/beast_{timestamp}.%(ext)s"

        ydl_opts = {
            'format': 'best[ext=mp4]/best', # Eng yaxshi MP4 format
            'outtmpl': out_template,
            'max_filesize': 48 * 1024 * 1024, # 48MB (Telegram limitidan bir oz kamroq)
            'quiet': True,
            'no_warnings': True,
            # TikTok suv belgisini olib tashlash va boshqa platformalar uchun headerlar
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)
                return file_path, info.get('title', 'Video')
        except Exception as e:
            logger.error(f"Yuklashda xato: {e}")
            return None, str(e)

    def clean_up(self, file_path):
        """Server xotirasini tozalash (yuklangandan keyin faylni o'chirish)"""
        if os.path.exists(file_path):
            os.remove(file_path)

beast = MediaBeast()
