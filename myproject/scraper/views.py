from django.shortcuts import render
from django.views.generic.base import (
    View,TemplateView,RedirectView,
)
from django.utils import timezone
from django.http import HttpResponse
from .scrapes.osaka.bears_scraper import bears_scraper
from .scrapes.osaka.sengoku_scraper import sengoku_scraper
from .scrapes.osaka.helluva_scraper import helluva_scraper
from .scrapes.osaka.fuzz_scraper import fuzz_scraper
from .scrapes.osaka.mele_scraper import mele_scraper
from .scrapes.osaka.socore_scraper import socore_scraper
from .scrapes.osaka.tora_scraper import tora_scraper
from .scrapes.osaka.hokage_scraper import hokage_scraper
from .scrapes.osaka.king_scraper import king_scraper
from .scrapes.osaka.fandango_scraper import fandango_scraper
from .models import Bears,Sengoku,Helluva,Fuzz,Mele,Socore,Tora,Hokage,King,Fandango,Anarky,Stomp
from .forms import MyForm

def scrape_view(request):
    bears_scraper()
    sengoku_scraper()
    helluva_scraper()
    fuzz_scraper()
    mele_scraper()
    socore_scraper()
    tora_scraper()
    hokage_scraper()
    king_scraper()
    fandango_scraper()
    print("Scraping executed")
    return HttpResponse("Scraping completed!")

def event_list(request):
    # データベースから全イベントを取得
    events = Fandango.objects.all().order_by('date')  # 日付順にソート
    return render(request, 'events/event_list.html', {'events': events})

class IndexView(View):
    
    def get(self,request,*args,**kwargs):
        my_form = MyForm()
        # 今日の日付を取得
        today = timezone.now().date()

        # 今日の日付と一致するレコードを取得
        bears_events = Bears.objects.filter(date=today)
        sengoku_events = Sengoku.objects.filter(date=today)
        helluva_events = Helluva.objects.filter(date=today)
        fuzz_events = Fuzz.objects.filter(date=today)
        mele_events = Mele.objects.filter(date=today)
        socore_events = Socore.objects.filter(date=today)
        tora_events = Tora.objects.filter(date=today)
        hokage_events = Hokage.objects.filter(date=today)
        king_events = King.objects.filter(date=today)
        fandango_events = Fandango.objects.filter(date=today)
        anarky_events = Anarky.objects.filter(date=today)
        stomp_events = Stomp.objects.filter(date=today)
        return render(request,'events/osaka.html',context={
            'date':'本日',
            'my_form':my_form,
            'bears_events':bears_events,
            'sengoku_events':sengoku_events,
            'helluva_events':helluva_events,
            'fuzz_events':fuzz_events,
            'mele_events':mele_events,
            'socore_events':socore_events,
            'tora_events':tora_events,
            'hokage_events':hokage_events,
            'king_events':king_events,
            'fandango_events':fandango_events,
            'anarky_events':anarky_events,
            'stomp_events':stomp_events,
        })
    
    def post(self,request,*args,**kwargs):
        my_form = MyForm(request.POST or None)
        if my_form.is_valid():
            date = my_form.cleaned_data['date']  # フォームから選択された日付を取得

            # 選択された日付に基づいてイベントを取得
            bears_events = Bears.objects.filter(date=date)
            sengoku_events = Sengoku.objects.filter(date=date)
            helluva_events = Helluva.objects.filter(date=date)
            fuzz_events = Fuzz.objects.filter(date=date)
            mele_events = Mele.objects.filter(date=date)
            socore_events = Socore.objects.filter(date=date)
            tora_events = Tora.objects.filter(date=date)
            hokage_events = Hokage.objects.filter(date=date)
            king_events = King.objects.filter(date=date)
            fandango_events = Fandango.objects.filter(date=date)
            anarky_events = Anarky.objects.filter(date=date)
            stomp_events = Stomp.objects.filter(date=date)
            return render(request,'events/osaka.html',context={
                'date':date,
                'my_form':my_form,
                'bears_events':bears_events,
                'sengoku_events':sengoku_events,
                'helluva_events':helluva_events,
                'fuzz_events':fuzz_events,
                'mele_events':mele_events,
                'socore_events':socore_events,
                'tora_events':tora_events,
                'hokage_events':hokage_events,
                'king_events':king_events,
                'fandango_events':fandango_events,
                'anarky_events':anarky_events,
                'stomp_events':stomp_events,
            })
        else:
            return render(request, 'events/osaka.html', context={
                'my_form': my_form,
            })