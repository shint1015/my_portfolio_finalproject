from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from chatbot.interface.api.serializers import ChatRequestSerializer
from chatbot.application.use_cases.ask_question import AskQuestionUseCase
from chatbot.application.policies import SimilarityPolicy
from chatbot.infrastructure.django.repositories import InMemoryChunkRepository
from chatbot.infrastructure.llm.openai_client import DummyLLMClient


class ChatView(APIView):
    def post(self, request):
        ser = ChatRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        usecase = AskQuestionUseCase(
            repo=InMemoryChunkRepository(),
            llm=DummyLLMClient(),
            policy=SimilarityPolicy(threshold=0.75),
        )

        result = usecase.execute(ser.validated_data["query"])
        return Response(result, status=status.HTTP_200_OK)