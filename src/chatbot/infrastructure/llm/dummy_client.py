class DummyLLMClient:
    def answer(self, system: str, user: str) -> str:
        return "I couldn’t find that directly, but I can give a general overview if you want."
