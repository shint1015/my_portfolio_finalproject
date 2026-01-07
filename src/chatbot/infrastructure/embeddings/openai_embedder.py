from django.conf import settings
from openai import OpenAI


class OpenAIEmbedder:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = getattr(settings, "OPENAI_EMBED_MODEL", "text-embedding-3-small")

    def embed(self, text: str) -> list[float]:
        response = self.client.embeddings.create(model=self.model, input=text)
        return response.data[0].embedding
