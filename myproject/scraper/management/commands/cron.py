from django.core.management.base import BaseCommand
import importlib
from django.http import HttpResponse
import traceback
import requests
from django.http import JsonResponse

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

class Command(BaseCommand):
    help = 'Scrape events from the website'

    def handle(self, *args, **kwargs):
        try:
            for module_name in [
                "hardrain_scraper",
            "paradice_scraper","bears_scraper", "sengoku_scraper", "helluva_scraper", "fuzz_scraper", 
            "mele_scraper", "socore_scraper", "tora_scraper", "hokage_scraper","fandango_scraper"]:
                module = importlib.import_module(f'scraper.scrapes.osaka.{module_name}')
                getattr(module, module_name)()

            # Successful scraping
            success_message = "Scraping executed successfully!"
            send_line_notify(success_message)

            print(success_message)
            print("Scraping completed!")  # または self.stdout.write("Scraping completed!")

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
            self.stderr.write("An error occurred during scraping.")
            self.stderr.write(error_message)
            self.stderr.write(stack_trace)
