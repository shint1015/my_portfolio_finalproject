import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from chatbot.interface.api.serializers import ChatRequestSerializer
from chatbot.application.use_cases.ask_question import AskQuestionUseCase
from chatbot.application.policies import SimilarityPolicy
from chatbot.infrastructure.django.repositories import PgVectorChunkRepository
from chatbot.infrastructure.llm.openai_client import OpenAILLMClient


SESSION_HISTORY_KEY = "chat_history"


def verify_recaptcha(token: str, action: str) -> tuple[bool, str]:
    if not settings.RECAPTCHA_SECRET_KEY:
        return False, "recaptcha_not_configured"

    payload = urlencode(
        {
            "secret": settings.RECAPTCHA_SECRET_KEY,
            "response": token,
        }
    ).encode("utf-8")
    req = Request(
        "https://www.google.com/recaptcha/api/siteverify",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    if not data.get("success"):
        return False, "recaptcha_failed"

    if data.get("action") != action:
        return False, "recaptcha_action_mismatch"

    score = float(data.get("score", 0))
    if score < settings.RECAPTCHA_MIN_SCORE:
        return False, "recaptcha_low_score"

    return True, ""


class ChatView(APIView):
    def post(self, request):
        ser = ChatRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        ok, reason = verify_recaptcha(
            ser.validated_data["recaptcha_token"],
            ser.validated_data["recaptcha_action"],
        )
        if not ok:
            return Response(
                {"detail": "reCAPTCHA verification failed.", "reason": reason},
                status=status.HTTP_400_BAD_REQUEST,
            )

        usecase = AskQuestionUseCase(
            repo=PgVectorChunkRepository(),
            llm=OpenAILLMClient(),
            policy=SimilarityPolicy(threshold=0.15),
        )

        query = ser.validated_data["query"]
        result = usecase.execute(query)

        history = request.session.get(SESSION_HISTORY_KEY, [])
        history = [
            *history,
            {"role": "user", "content": query, "sources": []},
            {
                "role": "assistant",
                "content": result["answer"],
                "sources": result["sources"],
            },
        ]
        request.session[SESSION_HISTORY_KEY] = history
        request.session.modified = True
        return Response(result, status=status.HTTP_200_OK)
