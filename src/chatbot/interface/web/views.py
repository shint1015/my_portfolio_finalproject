from django.conf import settings
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

SESSION_HISTORY_KEY = "chat_history"


def _get_history(request):
    return request.session.get(SESSION_HISTORY_KEY, [])


def _save_history(request, history):
    request.session[SESSION_HISTORY_KEY] = history
    request.session.modified = True


@require_http_methods(["GET"])
def chat_view(request):
    history = _get_history(request)
    return render(
        request,
        "chatbot/chat.html",
        {"history": history, "recaptcha_site_key": settings.RECAPTCHA_SITE_KEY},
    )


@require_http_methods(["GET"])
def home_view(request):
    return render(request, "chatbot/home.html")


@require_http_methods(["GET", "POST"])
def chat_reset_view(request):
    request.session.pop(SESSION_HISTORY_KEY, None)
    return redirect("chat")
