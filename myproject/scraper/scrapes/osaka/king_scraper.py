import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from django.core.files.storage import default_storage
from ...models import King  # Djangoモデルのインポート
import logging

def generate_url():
    """ 正しいURL形式（2025_3.htmlのような形式）を生成 """
    now = datetime.now()
    if now.month == 12:
        year, month = now.year + 1, 1
    else:
        year, month = now.year, now.month + 1
    return year, month, f"http://king-cobra.net/schedule/{year}_{month}.html"

def king_scraper():
    """ KING COBRAのスケジュールをスクレイピングし、データを保存する """
    print("------------king start----------------")
    
    year, month, url = generate_url()
    print(f"Scraping URL: {url}")

    try:
        headers = {"Accept-Charset": "Shift_JIS"}  # サーバーが UTF-8 を返さないように指示
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 404や500エラーを検出

        # `Shift_JIS` でデコード（これが正解）
        response_text = response.content.decode("shift_jis", errors="ignore")

        # BeautifulSoupで `Shift_JIS` を明示的に指定
        soup = BeautifulSoup(response_text, 'html.parser', from_encoding="shift_jis")

        # 確認用に最初の1000文字を表示（デバッグ）
        print(soup.prettify()[:1000])

        # イベントデータの取得
        for event_row in soup.find_all('tr'):
            try:
                # 日付取得
                date_cell = event_row.find('td', width="93")  # "93" は日付セルの width
                if not date_cell:
                    continue
                
                date_text = date_cell.get_text(strip=True)

                print(f"Raw Date Text: {date_text}")  # 文字化けしていないか確認

                # `3月1日` のような形式から日付を抽出
                match = re.search(r'(\d+)月(\d+)日', date_text)
                if not match:
                    print(f"Warning: Unable to extract date from {date_text}")
                    continue  # 日付が適切に取得できない場合スキップ

                day = int(match.group(2))  # "1" の部分を取得
                event_date = datetime(year, month, day)
                
                # 出演者や詳細情報の取得
                td_list = event_row.find_all("td")
                if len(td_list) < 4:  # tdの数が少ない場合はスキップ
                    continue
                
                title = td_list[1].get_text(strip=True).replace("『", "").replace("』", "")
                performers = td_list[2].get_text(separator="\n", strip=True).replace("■出演者", "")
                open_start = td_list[3].get_text(separator=" ", strip=True)
                ticket = td_list[4].get_text(separator=" ", strip=True).replace("・", "")

                # 空のデータをスキップ
                if not title:
                    print(f"Warning: Empty title for date {event_date}. Skipping...")
                    continue

                content = f"{open_start}\n{ticket}"

                # Djangoのモデルへ保存
                King.objects.update_or_create(
                    date=event_date,
                    defaults={
                        'title': title,
                        'performers': performers,
                        'content': content
                    }
                )
                print(f"Saved event: {title} on {event_date}")

            except Exception as inner_exception:
                print(f"Error processing event row at date '{date_text}': {inner_exception}")

    except requests.exceptions.RequestException as e:
        print(f"Failed to scrape data from {url}: {e}")

    print("------------king end----------------")
