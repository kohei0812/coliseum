import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from django.core.files.base import ContentFile
from urllib.parse import urljoin
from ...models import Hokage  # Adjust to your actual model name

def extract_event_date(date_text):
    match = re.search(r'(\d{4})\.(\d{1,2})\.(\d{1,2})', date_text)
    if match:
        year, month, day = map(int, match.groups())
        return datetime(year, month, day)
    return None

def save_image(image_url, event_title, max_length=50):
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        ext = image_url.split('.')[-1]
        file_name = f"{event_title.replace(' ', '_')[:max_length]}.{ext}"
        return ContentFile(response.content), file_name
    except Exception as e:
        print(f"Error fetching image from {image_url}: {e}")
    return None, None

def hokage_scraper():
    print("------------hokage start----------------")
    current_month = datetime.now().month
    current_year = datetime.now().year
    next_month = (current_month % 12) + 1
    next_year = current_year if next_month != 1 else current_year + 1
    url = f"http://musicbarhokage.net/schedule{next_month}_{next_year}.htm"
    
    response = requests.get(url)
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, 'html.parser')

    event_rows = soup.find_all('tr')[5:]  # Adjust if header rows exist
    events = []

    for row in event_rows:
        div_table = row.find('div', align='center')
        if not div_table:
            continue
        
        internal_table = div_table.find('table')
        if not internal_table:
            continue

        date_text = None
        title = ""
        performers = ""
        content_parts = []
        image_url = ""

        internal_rows = internal_table.find_all('tr')

        for idx, internal_row in enumerate(internal_rows):
            row_text = internal_row.get_text(strip=True)

            if idx == 0 and re.search(r'\d{4}\.\d{1,2}\.\d{1,2}', row_text):
                date_text = row_text.strip()

            if idx in {1, 2}:  # タイトルを2行から取得
                title += row_text + "\n"

            # コンテンツとパフォーマーを分ける
            if idx >= 3 and re.search(r'OPEN|START|Adv\.|Door\.', row_text):
                content_parts.append(row_text)
            elif idx >= 2:  # performers に全て追加
                performers_div = internal_row.find('p')
                if performers_div:
                    performers += performers_div.decode_contents() + "<br>"  # <br>を追加して改行情報を保持

            img_tag = internal_row.find('img')
            if img_tag and 'src' in img_tag.attrs:
                image_url = img_tag['src']

        # Adv.で始まる行を除外
        performers = [p for p in performers.split("<br>") if not p.startswith("Adv.")][0]
        # HTML をパース
        soup = BeautifulSoup(performers, 'html.parser')

        # strong タグを取得してテキストを抽出
        performers = soup.find('strong')

        # タグをなくして改行を保持
        if performers:
            performers_text = performers.get_text(separator="\n").strip()  # 改行を\nに変換
        else:
            performers_text = ""
            
        event_date = extract_event_date(date_text)
        title = title.strip()  # タイトルを整形
        content = "\n".join(content_parts).strip()

        if event_date is None:
            print(f"No valid date found for event: {date_text}")
            continue

        event_data = {
            'date': event_date,
            'title': title,
            'performers': performers_text,  # パフォーマー部分を正しく格納
            'content': content,
            'image_url': image_url
        }
        events.append(event_data)

    for event in events:
        try:
            event_obj, created = Hokage.objects.update_or_create(
                date=event['date'],
                defaults={
                    'title': event['title'],
                    'content': event['content'],
                    'performers': event['performers'],
                }
            )

            if created or not event_obj.image:
                if event['image_url']:
                    image_url = urljoin(url, event['image_url'])
                    image_content, image_name = save_image(image_url, event['title'])
                    if image_content:
                        event_obj.image.save(image_name, image_content)
                        print(f"Image saved for event '{event['title']}'")

            if created:
                print(f"Event '{event['title']}' created successfully")
            else:
                print(f"Event '{event['title']}' updated successfully")
        except Exception as e:
            print(f"Error saving event '{event['title']}': {e}")

    print("------------hokage end----------------")
