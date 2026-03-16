from groq import Groq
from config import config

class MasterBrain:
    def __init__(self):
        # Katta harfli Groq to'g'ridan-to'g'ri chaqiriladi
        self.client = Groq(api_key=config.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"

    def get_ai_response(self, user_id, text):
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Sen Shaxzod yaratgan Master AI Infinity botsan. O'zbek tilida mukammal javob berasan."},
                    {"role": "user", "content": text}
                ],
                model=self.model,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"🧠 AI tizimida xatolik: {str(e)}"

brain = MasterBrain()
