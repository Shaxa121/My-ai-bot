from googletrans import Translator
import logging

logger = logging.getLogger("TranslatorModule")

class UniversalTranslator:
    def __init__(self):
        self.translator = Translator()

    def translate_text(self, text, target_lang='uz'):
        """
        Matnni avtomatik aniqlab, ko'rsatilgan tilga o'giradi.
        """
        try:
            if not text:
                return "Bo'sh matn yuborildi."
            
            # Matn uzunligini tekshirish (Google limitlari uchun)
            if len(text) > 4500:
                text = text[:4500]

            result = self.translator.translate(text, dest=target_lang)
            return {
                'original': text,
                'translated': result.text,
                'detected': result.src
            }
        except Exception as e:
            logger.error(f"Tarjimada xato: {e}")
            return f"❌ Tarjima modulida nosozlik: {str(e)}"

translator = UniversalTranslator()
