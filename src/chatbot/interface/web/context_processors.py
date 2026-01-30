from django.conf import settings


def resume_url(request):
    return {"resume_url": settings.RESUME_URL}
