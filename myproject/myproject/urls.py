from django.contrib import admin
from django.urls import path
from scraper.views import scrape_view,event_list
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('scrape/', scrape_view, name='scrape'),
    path('events/', event_list, name='event_list'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)