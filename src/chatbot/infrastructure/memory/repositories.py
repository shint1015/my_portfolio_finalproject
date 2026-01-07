from typing import Iterable, Sequence

from chatbot.domain.ports import RetrievedChunk


class InMemoryChunkRepository:
    def __init__(self, chunks: Iterable[RetrievedChunk] | None = None):
        self._chunks = list(chunks or [])

    def search(self, query: str, k: int = 4) -> Sequence[RetrievedChunk]:
        return self._chunks[:k]
