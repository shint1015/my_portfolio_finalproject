from chatbot.domain.ports import ChunkRepository, LLMClient, RetrievedChunk
from chatbot.application.policies import SimilarityPolicy


SYSTEM_PROMPT = """You must answer using ONLY the provided context.
If the answer is not in the context, say: "I don’t know based on my data."
Do not guess. Include sources (source names)."""

class AskQuestionUseCase:
    def __init__(self, repo: ChunkRepository, llm: LLMClient, policy: SimilarityPolicy):
        self.repo = repo
        self.llm = llm
        self.policy = policy

    def execute(self, question: str) -> dict:
        chunks = list(self.repo.search(question, k=4))
        if self.policy.is_insufficient(chunks):
            return {
                "answer": "I don’t know based on my data.",
                "sources": [],
            }
        
        context = "\n\n".join([f"[{c['source']}] {c['content']}" for c in chunks])
        user = f"context:\n{context}\n\nQuestion:\n{question}"
        answer = self.llm.answer(SYSTEM_PROMPT, user)
        sources = sorted(set(c["source"] for c in chunks))
        return {
            "answer": answer,
            "sources": sources,
        }
