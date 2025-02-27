import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from django.utils import timezone
from django.core.files.base import ContentFile
from ...models import Bears

# サポートされていない文字を削除する関数
def remove_unsupported_chars(text):
    return re.sub(r'[^\u0000-\uFFFF]', '', text)  # BMP外のUnicode文字（絵文字など）を削除

def bears_scraper():
    print("------------Bears start----------------")
    url = "https://namba-bears.main.jp/schedule.html"
    response = requests.get(url)
    print("URL fetched")
    soup = BeautifulSoup(response.content, 'html.parser')
    base_url = "https://namba-bears.main.jp/"
    
    # 現在の年・月
    today = timezone.now()
    current_year = today.year
    current_month = today.month

    for table in soup.find_all('table'):
        date_text = table.find('th').get_text(strip=True)
        print(f"Processing event for date: {date_text}")
        
        # 日付のみを抽出
        date_match = re.search(r'(\d{1,2})月(\d{1,2})日', date_text)
        if not date_match:
            continue  # 日付が見つからない場合はスキップ
        
        month, day = map(int, date_match.groups())  # 月と日を抽出
        print(f"Extracted date: {month}月{day}日")
        
        # 年を決定（イベントの月が現在の月より前なら翌年）
        event_year = current_year if month >= current_month else current_year + 1

        try:
            event_date = datetime(year=event_year, month=month, day=day)
        except ValueError:
            continue  # 日付の形式が正しくない場合はスキップ

        # イベントの時間（open/start）を抽出
        time_match = re.search(r'open\d{1,2}:\d{2}.*start\d{1,2}:\d{2}', date_text)
        event_time = time_match.group(0) if time_match else "No time info"

        # イベントのタイトルを取得
        title = table.find('p').get_text(strip=True) if table.find('p') else "No Title"
        title = remove_unsupported_chars(title)  # 文字除去

        # 出演者情報を取得
        performers = []
        performer_tags = table.find_all('td', width="610")  # 出演者情報が入っているタグを探す
        if performer_tags:
            for performer_tag in performer_tags:
                performers.append(remove_unsupported_chars(performer_tag.get_text(strip=True)))  # 文字除去
        performers_text = "\n".join(performers) if performers else "No performers listed"

        # コンテンツ情報を取得
        content = table.find('td', width="610").get_text(separator="\n", strip=True)
        content = remove_unsupported_chars(content)  # 文字除去

        # Remove the first line of the content
        content_lines = content.split("\n")
        if len(content_lines) > 1:
            content = "\n".join(content_lines[1:])
        else:
            content = "No content available"

        # 画像の取得
        image_tag = table.find('img')
        image_url = image_tag['src'] if image_tag else None
        if image_url and not image_url.startswith(('http://', 'https://')):
            image_url = base_url + image_url.lstrip('/')  # ベースURLと相対パスを結合
        
        # 出力情報を確認
        print(f"Title: {title}")
        print(f"Performers: {performers_text}")
        print(f"Content: {content}")
        print(f"Event Date: {event_date}")  # 修正ポイント: 日付の出力
        print(f"Event Time: {event_time}")
        print(f"Image URL: {image_url}")

        # 同じ日付のイベントを取得または作成
        event, created = Bears.objects.update_or_create(
            date=event_date,
            defaults={
                'title': title,
                'content': content,
                # 'performers': performers_text,
            }
        )

        # チラシの画像を保存
        if image_url:
            if not event.image:  # 画像が存在しない場合
                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    image_file_name = os.path.basename(image_url)
                    event.image.save(image_file_name, ContentFile(image_response.content))
                    print(f"Image saved for event '{title}'")
            else:
                print(f"Image already exists for event '{title}', skipping image save.")

        # 上書きした場合のメッセージ
        if created:
            print(f"Event '{title}' created successfully")
        else:
            print(f"Event '{title}' updated successfully")
    print("------------Bears end----------------")