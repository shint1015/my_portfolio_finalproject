from chatbot.domain.ports import RetrievedChunk

class InMemoryChunkRepository:
    def __init__(self):
        self.data: list[RetrievedChunk] = [
            {
                "content": "My name is Shintaro Miyata. I work as a backend/full-stack engineer.",
                "source": "profile.txt",
                "score": 0.95,
            },
            {
                "content": "Main skills: Python, Django, Laravel, Go, TypeScript, React.",
                "source": "skills.txt",
                "score": 0.90,
            },
        ]
    def search(self, query: str, k:int = 4):
        return self.data[:k]
    
