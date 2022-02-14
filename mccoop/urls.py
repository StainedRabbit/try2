from django.contrib import admin
from django.urls import path, include

# Use static() to add url mapping to serve static files during development (only)
from django.conf import settings


urlpatterns = [
    path("grappelli/", include("grappelli.urls")),  # grappelli URLS
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", include("app.urls")),
]


if settings.ENVIRONMENT == "development":
    urlpatterns.append(path("__debug__/", include("debug_toolbar.urls")))

from django.conf.urls.static import static

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
