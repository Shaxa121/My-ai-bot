import groq
import logging
from config import config

class MasterBrain:
    def __init__(self):
        # Siz bergan API kalitni config orqali oladi
        self.client = groq.Groq(api_key=config.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"
        self.history = {}

    def get_response(self, user_id, user_text):
        """
        AI mantiqi: Foydalanuvchi tarixini saqlaydi va aqlli javob beradi.
        """
        try:
            if user_id not in self.history:
                self.history[user_id] = [
                    {"role": "system", "content": "Siz Shaxzod tomonidan yaratilgan Master AI Infinity botisiz. O'zbek tilida mukammal javob berasiz."}
                ]

            self.history[user_id].append({"role": "user", "content": user_text})

            # Groq so'rovi
            chat_completion = self.client.chat.completions.create(
                messages=self.history[user_id],
                model=self.model,
                temperature=0.8,
                max_tokens=3000
            )

            reply = chat_completion.choices[0].message.content
            self.history[user_id].append({"role": "assistant", "content": reply})

            # Xotirani boshqarish (Oxirgi 10 ta suhbatni eslab qoladi)
            if len(self.history[user_id]) > 20:
                self.history[user_id] = [self.history[user_id][0]] + self.history[user_id][-10:]

            return reply
        except Exception as e:
            return f"🆘 AI tizimida xatolik: {str(e)}"

brain = MasterBrain()
