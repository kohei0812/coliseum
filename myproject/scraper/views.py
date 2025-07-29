from django.shortcuts import render
from django.views.generic.base import (
    View,TemplateView,RedirectView,
)
from django.utils import timezone
from django.http import HttpResponse
import importlib
from .models import Bears,Sengoku,Helluva,Fuzz,Mele,Socore,Tora,Hokage,King,Fandango,Anarky,Stomp,Paradice,Hardrain
from .forms import MyForm
from datetime import date as dt_date
import traceback
import requests
from django.http import JsonResponse, JsonResponse
import time
import json
import sys
import io


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
    output_buffer = io.StringIO()  # 標準出力をキャプチャするバッファ
    sys.stdout = output_buffer  # 標準出力をリダイレクト
    try:
        for module_name in [
             "tora_scraper",
            "paradice_scraper","bears_scraper", "sengoku_scraper", "helluva_scraper", "fuzz_scraper", 
            "mele_scraper", "socore_scraper", "hokage_scraper","fandango_scraper","hardrain_scraper",
            ]:
            module = importlib.import_module(f'.scrapes.osaka.{module_name}', __package__)
            getattr(module, module_name)()
        print("Scraping executed")
        sys.stdout = sys.__stdout__
        return HttpResponse(f"Scraping completed!\n\nOutput:\n{output_buffer.getvalue()}", content_type="text/plain")
    
    except Exception as e:
        sys.stdout = sys.__stdout__  # 標準出力を元に戻す
        # エラーメッセージとトレースバックを取得
        error_message = f"An error occurred: {str(e)}"
        stack_trace = traceback.format_exc()  # エラートレースバックを取得

         # エラーメッセージとトレースバックを取得し、キャプチャした出力と共に表示
        error_output = output_buffer.getvalue()
        full_error_message = f"Scraping failed.\n\nOutput:\n{error_output}\n\nError: {error_message}\nTraceback:\n{stack_trace}"

        print(full_error_message)  # エラーをログに出力
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
    events = Tora.objects.all().order_by('date')  # 日付順にソート
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
        paradice_events = Paradice.objects.filter(date=today)
        hardrain_events = Hardrain.objects.filter(date=today)
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
            'paradice_events':paradice_events,
            'hardrain_events':hardrain_events,
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
            paradice_events = Paradice.objects.filter(date=date)
            hardrain_events = Hardrain.objects.filter(date=date)
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
                'paradice_events':paradice_events,
                'hardrain_events':hardrain_events,
                'timestamp': timestamp,
            })
        else:
            return render(request, 'events/osaka.html', context={
                'my_form': my_form,
            })

class IndexAPIView(View):

    def get(self, request, *args, **kwargs):
        """本日のイベントを取得"""
        today = timezone.now().date()
        timestamp = str(int(time.time()))

        events_data = {
            'date': '本日',
            'bears_events': list(Bears.objects.filter(date=today).values()),
            'sengoku_events': list(Sengoku.objects.filter(date=today).values()),
            'helluva_events': list(Helluva.objects.filter(date=today).values()),
            'fuzz_events': list(Fuzz.objects.filter(date=today).values()),
            'mele_events': list(Mele.objects.filter(date=today).values()),
            'socore_events': list(Socore.objects.filter(date=today).values()),
            'tora_events': list(Tora.objects.filter(date=today).values()),
            'hokage_events': list(Hokage.objects.filter(date=today).values()),
            'king_events': list(King.objects.filter(date=today).values()),
            'fandango_events': list(Fandango.objects.filter(date=today).values()),
            'anarky_events': list(Anarky.objects.filter(date=today).values()),
            'stomp_events': list(Stomp.objects.filter(date=today).values()),
            'paradice_events': list(Paradice.objects.filter(date=today).values()),
            'hardrain_events': list(Hardrain.objects.filter(date=today).values()),
            'timestamp': timestamp,
        }

        response = JsonResponse(events_data, safe=False)
        response["Access-Control-Allow-Origin"] = "*"  # CORS許可
        response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    def post(self, request, *args, **kwargs):
        """指定された日付のイベントを取得"""
        try:
            data = json.loads(request.body)  # JSONリクエストをパース
            selected_date = data.get('date')  # 選択された日付

            if not selected_date:
                return JsonResponse({"error": "日付が指定されていません"}, status=400)

            selected_date = dt_date.fromisoformat(selected_date)  # YYYY-MM-DD の形式に変換
            today = dt_date.today()
            timestamp = str(int(time.time()))

            date_display = "本日" if selected_date == today else str(selected_date)

            events_data = {
                'date': date_display,
                'bears_events': list(Bears.objects.filter(date=selected_date).values()),
                'sengoku_events': list(Sengoku.objects.filter(date=selected_date).values()),
                'helluva_events': list(Helluva.objects.filter(date=selected_date).values()),
                'fuzz_events': list(Fuzz.objects.filter(date=selected_date).values()),
                'mele_events': list(Mele.objects.filter(date=selected_date).values()),
                'socore_events': list(Socore.objects.filter(date=selected_date).values()),
                'tora_events': list(Tora.objects.filter(date=selected_date).values()),
                'hokage_events': list(Hokage.objects.filter(date=selected_date).values()),
                'king_events': list(King.objects.filter(date=selected_date).values()),
                'fandango_events': list(Fandango.objects.filter(date=selected_date).values()),
                'anarky_events': list(Anarky.objects.filter(date=selected_date).values()),
                'stomp_events': list(Stomp.objects.filter(date=selected_date).values()),
                'paradice_events': list(Paradice.objects.filter(date=selected_date).values()),
                'hardrain_events': list(Hardrain.objects.filter(date=selected_date).values()),
                'timestamp': timestamp,
            }

            response = JsonResponse(events_data, safe=False)
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type"
            return response

        except Exception as e:
            response = JsonResponse({"error": f"データ取得に失敗しました: {str(e)}"}, status=500)
            response["Access-Control-Allow-Origin"] = "*"
            return response