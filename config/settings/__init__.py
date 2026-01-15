import os

ENVIRONMENT = os.environ.get("DJANGO_ENV", "development").lower()

if ENVIRONMENT == "production":
    from .prod import *  # noqa: F403
else:
    from .dev import *  # noqa: F403
