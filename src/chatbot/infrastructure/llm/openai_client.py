from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

class OpenAILLMClient:
    model = getattr(settings, "OPENAI_CHAT_MODEL", "gpt-5.1-mini")

    def answer(self, system: str, user: str) -> str:
        r = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return r.choices[0].message.content
