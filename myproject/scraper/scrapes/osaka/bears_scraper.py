import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from django.core.files.base import ContentFile
from ...models import Bears

def bears_scraper():
    url = "https://namba-bears.main.jp/schedule.html"
    response = requests.get(url)
    print("URL fetched")
    soup = BeautifulSoup(response.content, 'html.parser')
    base_url = "https://namba-bears.main.jp/"
    
    for table in soup.find_all('table'):
        date_text = table.find('th').get_text(strip=True)
        print(f"Processing event for date: {date_text}")
        
        # 日付のみを抽出
        date_match = re.search(r'\d{1,2}月\d{1,2}日', date_text)
        if not date_match:
            continue  # 日付が見つからない場合はスキップ
        
        date_str = date_match.group(0)
        print(f"Extracted date: {date_str}")
        
        try:
            event_date = datetime.strptime(date_str, "%m月%d日").replace(year=2024)
        except ValueError:
            continue  # 日付の形式が正しくない場合はスキップ

        # イベントの時間（open/start）を抽出
        time_match = re.search(r'open\d{1,2}:\d{2}.*start\d{1,2}:\d{2}', date_text)
        event_time = time_match.group(0) if time_match else "No time info"

        # イベントのタイトルを取得
        title = table.find('p').get_text(strip=True) if table.find('p') else "No Title"

        # 出演者情報を取得
        performers = []
        performer_tags = table.find_all('td', width="610")  # 出演者情報が入っているタグを探す
        if performer_tags:
            for performer_tag in performer_tags:
                performers.append(performer_tag.get_text(strip=True))
        performers_text = "\n".join(performers) if performers else "No performers listed"

        # コンテンツ情報を取得
        content = table.find('td', width="610").get_text(separator="\n", strip=True)

        # 画像の取得
        image_tag = table.find('img')
        image_url = image_tag['src'] if image_tag else None
        if image_url and not image_url.startswith(('http://', 'https://')):
            image_url = base_url + image_url.lstrip('/')  # ベースURLと相対パスを結合
        
        # 出力情報を確認
        print(f"Title: {title}")
        print(f"Performers: {performers_text}")
        print(f"Content: {content}")
        print(f"Event Time: {event_time}")
        print(f"Image URL: {image_url}")

        # 同じ日付のイベントを取得または作成
        event, created = Bears.objects.update_or_create(
            date=event_date,
            defaults={
                'title': title,
                'content': content,
                'performers': performers_text,
            }
        )

        # チラシの画像を保存
        if image_url:
            # 既存のイベントに画像があるかチェック
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
