from typing import Protocol, Sequence, TypedDict


class RetrievedChunk(TypedDict):
    content: str
    source: str
    score: float


class ChunkRepository(Protocol):
    def search(self, query: str, k: int) -> Sequence[RetrievedChunk]: ...


class LLMClient(Protocol):
    def answer(self, system: str, user: str) -> str: ...