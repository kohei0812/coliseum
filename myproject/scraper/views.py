from django.shortcuts import render

from django.http import HttpResponse
from .scrapes.osaka.bears_scraper import bears_scraper
from .scrapes.osaka.sengoku_scraper import sengoku_scraper
from .scrapes.osaka.helluva_scraper import helluva_scraper
from .scrapes.osaka.fuzz_scraper import fuzz_scraper
from .scrapes.osaka.mele_scraper import mele_scraper
from .scrapes.osaka.socore_scraper import socore_scraper
from .scrapes.osaka.tora_scraper import tora_scraper
from .scrapes.osaka.hokage_scraper import hokage_scraper
from .models import Bears,Sengoku,Helluva,Fuzz,Mele,Socore,Tora,Hokage

def scrape_view(request):
    # bears_scraper()
    # sengoku_scraper()
    # helluva_scraper()
    # fuzz_scraper()
    # mele_scraper()
    # socore_scraper()
    # tora_scraper()
    hokage_scraper()
    print("Scraping executed")
    return HttpResponse("Scraping completed!")

def event_list(request):
    # データベースから全イベントを取得
    events = Hokage.objects.all().order_by('date')  # 日付順にソート
    return render(request, 'events/event_list.html', {'events': events})