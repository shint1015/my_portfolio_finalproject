from chatbot.domain.ports import RetrievedChunk

class SimilarityPolicy:
    def __init__(self, threshold: float = 0.75):
        self.threshold = threshold
    def is_insufficient(self, chunks: list[RetrievedChunk]):
        if not chunks:
            return True
        best = max(c["score"] for c in chunks)
        return best < self.threshold