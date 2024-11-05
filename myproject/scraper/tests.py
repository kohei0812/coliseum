from django.test import TestCase

# Create your tests here.
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from ...models import King  # Djangoモデルのインポート

# スクレイピング用のURLを生成
def generate_url():
    now = datetime.now()
    if now.month == 12:
        year, month = now.year + 1, 1
    else:
        year, month = now.year, now.month + 1
    return year, month, f"http://king-cobra.net/schedule/{year}_{month:02}.html"

def king_scraper():
    year, month, url = generate_url()
    try:
        response = requests.get(url)
        response.encoding = 'shift_jis'  # 文字エンコーディングの指定
        soup = BeautifulSoup(response.text, 'html.parser')

        for event_row in soup.find_all('tr'):
            try:
                # 日付の抽出
                date_cell = event_row.find('td', width="83")
                if not date_cell:
                    continue  # 日付が見つからない場合はスキップ
                
                date_text = date_cell.get_text(strip=True)

                # 日付が空でないことを確認
                if not date_text:
                    continue  # 日付が空の場合はスキップ

                # 日付を正規化
                # 例: '11月1日-Fri-' を '2024-11-01' に変換
                if '月' in date_text and '日' in date_text:
                    # 曜日を除去
                    clean_date_text = date_text.split('-')[0]  # 先頭の部分を取得
                    clean_date_text = clean_date_text.replace('月', '-').replace('日', '').strip()  # '11-1' 取得
                    date_str = f"{year}-{clean_date_text.zfill(2)}"  # '2024-11-01' に変換

                else:
                    continue  # 日付形式が不正な場合はスキップ
                
                # datetimeオブジェクトの生成
                event_date = datetime.strptime(date_str, "%Y-%m-%d")

                # 日付が正しく解析できているか確認
                if not event_date:
                    print(f"Could not parse date from '{date_str}'. Skipping.")
                    continue  # 日付の解析に失敗した場合はスキップ

                # タイトルの抽出
                title_cell = date_cell.find_next('td')
                title = title_cell.get_text(strip=True).replace("『", "").replace("』", "")

                # 出演者の抽出
                performers_cell = title_cell.find_next('td')
                performers = performers_cell.get_text(separator="\n", strip=True).replace("■出演者", "")
                
                # 開場・開演時間の抽出
                open_start_cell = performers_cell.find_next('td')
                open_start = open_start_cell.get_text(separator=" ", strip=True)
                
                # チケット料金の抽出
                ticket_cell = open_start_cell.find_next('td')
                ticket = ticket_cell.get_text(separator=" ", strip=True).replace("・", "")
                
                # contentにまとめる
                content = f"{open_start}\n{ticket}"
                
                # イベント情報の保存（既存の日付のデータがある場合は上書き）
                King.objects.update_or_create(
                    date=event_date,
                    defaults={
                        'title': title,
                        'performers': performers,
                        'content': content
                    }
                )
                print(f"Saved event: {title} on {event_date}")  # 成功したイベントのログ
            except Exception as inner_exception:
                print(f"Error processing event row at date '{date_text}': {inner_exception}")

    except Exception as outer_exception:
        print(f"Failed to scrape data from {url}: {outer_exception}")

# 例: スクレイピング関数を呼び出す
if __name__ == "__main__":
    king_scraper()
