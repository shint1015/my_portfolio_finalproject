from django.urls import path

from chatbot.interface.web.views import chat_reset_view, chat_view, home_view, introduction_view

urlpatterns = [
    path("", home_view, name="home"),
    path("introduction/", introduction_view, name="introduction"),
    path("chats/", chat_view, name="chat"),
    path("chat/", chat_view, name="chat_legacy"),
    path("chat/reset/", chat_reset_view, name="chat_reset"),
]
