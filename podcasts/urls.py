from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from podcasts.views import ITunesRSSView

urlpatterns = [
    path(
        "<slug:slug>-<str:rss_type>.rss", ITunesRSSView.as_view(), name="rss",
    )
]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
