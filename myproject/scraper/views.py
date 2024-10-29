from django.shortcuts import render

from django.http import HttpResponse
from .scrapes.osaka.bears_scraper import bears_scraper
from .scrapes.osaka.sengoku_scraper import sengoku_scraper
from .models import Bears,Sengoku

def scrape_view(request):
    # bears_scraper()
    # sengoku_scraper()
    print("Scraping executed")
    return HttpResponse("Scraping completed!")

def event_list(request):
    # データベースから全イベントを取得
    events = Sengoku.objects.all().order_by('date')  # 日付順にソート
    return render(request, 'events/event_list.html', {'events': events})