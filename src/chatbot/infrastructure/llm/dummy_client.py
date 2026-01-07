class DummyLLMClient:
    def answer(self, system: str, user: str) -> str:
        return "I don’t know based on my data."
