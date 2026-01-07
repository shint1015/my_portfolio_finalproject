from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from chatbot.application.policies import SimilarityPolicy
from chatbot.application.use_cases.ask_question import AskQuestionUseCase
from chatbot.infrastructure.django.repositories import PgVectorChunkRepository
from chatbot.infrastructure.llm.openai_client import OpenAILLMClient


SESSION_HISTORY_KEY = "chat_history"


def _get_history(request):
    return request.session.get(SESSION_HISTORY_KEY, [])


def _save_history(request, history):
    request.session[SESSION_HISTORY_KEY] = history
    request.session.modified = True


@require_http_methods(["GET", "POST"])
def chat_view(request):
    history = _get_history(request)

    if request.method == "POST":
        message = request.POST.get("message", "").strip()
        if message:
            history = [
                *history,
                {"role": "user", "content": message, "sources": []},
            ]

            usecase = AskQuestionUseCase(
                repo=PgVectorChunkRepository(),
                llm=OpenAILLMClient(),
                policy=SimilarityPolicy(threshold=0.75),
            )
            result = usecase.execute(message)

            history = [
                *history,
                {
                    "role": "assistant",
                    "content": result["answer"],
                    "sources": result["sources"],
                },
            ]
            _save_history(request, history)
            return redirect("chat")

    return render(request, "chatbot/chat.html", {"history": history})


@require_http_methods(["GET", "POST"])
def chat_reset_view(request):
    request.session.pop(SESSION_HISTORY_KEY, None)
    return redirect("chat")
