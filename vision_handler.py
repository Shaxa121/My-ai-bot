import groq
import base64
from config import config

class VisionHandler:
    def __init__(self):
        self.client = groq.Groq(api_key=config.GROQ_API_KEY)
        self.model = "llama-3.2-11b-vision-preview"

    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def analyze_image(self, image_path, prompt="Ushbu rasmda nimalar bor?"):
        try:
            base64_image = self.encode_image(image_path)
            
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                model=self.model,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"👁 Ko'rish modulida xato: {str(e)}"

vision = VisionHandler()
