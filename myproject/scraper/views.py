from django.shortcuts import render
from django.views.generic.base import (
    View,TemplateView,RedirectView,
)
from django.utils import timezone
from django.http import HttpResponse
import importlib
from .models import Bears,Sengoku,Helluva,Fuzz,Mele,Socore,Tora,Hokage,King,Fandango,Anarky,Stomp
from .forms import MyForm
from datetime import date as dt_date
import traceback
import requests
from django.http import JsonResponse
import time
# LINE Messaging APIに通知を送るための関数
def send_line_notify(message):
    url = "https://api.line.me/v2/bot/message/push"
    token = 'VS27YWarvMTBRxgeDXDLxY9CarB0DU5f0BiEPG5OKmnpWWPNOmmPk3Zh0f21ryKTwR18RxeOfB/0r6It14d+rFb2Qiz4u42JZB7mRGpMS7sAvd2b1v6sD0xfqP5ecYmtocESh104D33SMnOK73kxdgdB04t89/1O/w1cDnyilFU='  # ここにMessaging APIのアクセストークンを記述
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }

    # 送信するメッセージ
    payload = {
        "to": "keyserant",  # 通知を送りたいユーザーのID
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }

    # POSTリクエストを送信
    response = requests.post(url, headers=headers, json=payload)
    return response.status_code

def scrape_view(request):
    try:
        for module_name in [
            "bears_scraper", "sengoku_scraper", "helluva_scraper", "fuzz_scraper", 
            "mele_scraper", "socore_scraper", "tora_scraper", "hokage_scraper", 
            "king_scraper", "fandango_scraper"]:
            module = importlib.import_module(f'.scrapes.osaka.{module_name}', __package__)
            getattr(module, module_name)()
        print("Scraping executed")
        return HttpResponse("Scraping completed!")
    except Exception as e:
        # エラーメッセージとトレースバックを取得
        error_message = f"An error occurred: {str(e)}"
        stack_trace = traceback.format_exc()  # エラートレースバックを取得

        # エラーメッセージとトレースバックをコンソールに出力
        print(f"Error: {error_message}")
        print(f"Traceback:\n{stack_trace}")

        # LINEに通知
        line_message = f"Error in scrape_view:\n{error_message}\n\n{stack_trace}"
        send_line_notify(line_message)

        # エラーが発生した場合、通知用のレスポンスを返す
        return JsonResponse({
            "message": "An error occurred during scraping.",
            "error": error_message,
            "traceback": stack_trace
        }, status=500)
        
def event_list(request):
    # データベースから全イベントを取得
    events = Fandango.objects.all().order_by('date')  # 日付順にソート
    return render(request, 'events/event_list.html', {'events': events})

class IndexView(View):
    
    def get(self,request,*args,**kwargs):
        my_form = MyForm()
        # 今日の日付を取得
        today = timezone.now().date()
        timestamp = str(int(time.time()))
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
            'timestamp': timestamp,
        })
    
    def post(self,request,*args,**kwargs):
        my_form = MyForm(request.POST or None)
        if my_form.is_valid():
            date = my_form.cleaned_data['date']  # フォームから選択された日付を取得

            # 今日の日付を取得
            today = dt_date.today()
            timestamp = str(int(time.time()))
            # 日付が今日の場合は「本日」に置き換える
            date_display = "本日" if date == today else date
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
                'date':date_display,
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
                'timestamp': timestamp,
            })
        else:
            return render(request, 'events/osaka.html', context={
                'my_form': my_form,
            })