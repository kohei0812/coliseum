from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
from scraper.views import scrape_view,event_list,IndexView,IndexAPIView
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language

urlpatterns = [
    path('test/', lambda request: HttpResponse("Django is working!")),
    path('admin/', admin.site.urls),
    path('scrape/', scrape_view, name='scrape'),
    path('events/', event_list, name='event_list'),
    path('', IndexView.as_view(), name='index'),
    path('api/index/', IndexAPIView.as_view(), name='index_api'),
]
urlpatterns += i18n_patterns(
    path('set-language/', set_language, name='set_language'),  # 修正ポイント: set_language 関数を直接渡す
)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)