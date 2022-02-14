import os

ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")


if ENVIRONMENT == "development":
    from .development import *
elif ENVIRONMENT == "production":
    from .production import *
