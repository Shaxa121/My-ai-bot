import groq  # To'g'ridan-to'g'ri kutubxonani o'zini chaqiramiz
from config import config

class MasterBrain:
    def __init__(self):
        # Bu yerda groq.Groq deb chaqiramiz
        self.client = groq.Groq(api_key=config.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"

    def get_ai_response(self, user_id, text):
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "user", "content": text}
                ],
                model=self.model,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"AI xatosi: {str(e)}"

brain = MasterBrain()
