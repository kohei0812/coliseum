from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
from scraper.views import scrape_view,event_list,IndexView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('test/', lambda request: HttpResponse("Django is working!")),
    path('admin/', admin.site.urls),
    path('scrape/', scrape_view, name='scrape'),
    path('events/', event_list, name='event_list'),
    path('', IndexView.as_view(), name='index'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)