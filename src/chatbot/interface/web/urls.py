from django.urls import path

from chatbot.interface.web.views import chat_reset_view, chat_view

urlpatterns = [
    path("", chat_view, name="chat"),
    path("reset/", chat_reset_view, name="chat_reset"),
]
