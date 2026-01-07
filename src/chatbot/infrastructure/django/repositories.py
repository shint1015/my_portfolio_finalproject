from pgvector.django import CosineDistance

from chatbot.models import Chunk
from chatbot.infrastructure.embeddings.openai_embedder import OpenAIEmbedder

class PgVectorChunkRepository:
    def __init__(self):
        self.embedder = OpenAIEmbedder()

    def search(self, query: str, k: int = 4):
        q_emb = self.embedder.embed(query)

        # cosine_distance: 小さいほど近い
        qs = (
            Chunk.objects
            .annotate(distance=CosineDistance("embedding", q_emb))
            .order_by("distance")
            .values("content", "source", "distance")[:k]
        )

        results = []
        for row in qs:
            # distance -> score（暫定変換。0に近いほど良い）
            # ざっくり score = 1 - distance（負なら0に丸め）
            score = max(0.0, 1.0 - float(row["distance"]))
            results.append(
                {"content": row["content"], "source": row["source"], "score": score}
            )
        return results
