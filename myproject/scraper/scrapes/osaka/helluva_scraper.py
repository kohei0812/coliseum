import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from django.core.files.base import ContentFile
from urllib.parse import urljoin

from ...models import Helluva  # 適切なモデル名に変更してください

def extract_event_date(date_text):
    match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日[\s（(]*(日|月|火|水|木|金|土|日祝)[）)]*', date_text)
    if match:
        year, month, day = map(int, match.groups()[:3])
        return datetime(year, month, day)
    return None

def save_image(image_url, event_title):
    """画像のURLから画像を保存します。"""
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        ext = image_url.split('.')[-1]
        file_name = f"{event_title.replace(' ', '_')}.{ext}"
        return ContentFile(response.content), file_name
    except Exception as e:
        print(f"Error fetching image from {image_url}: {e}")
    return None, None

def sanitize_content(content):
    """pタグとaタグを除去し、テキストと改行情報のみを返す。"""
    soup = BeautifulSoup(content, 'html.parser')
    for p in soup.find_all('p'):
        p.unwrap()  # pタグを取り除く
    for a in soup.find_all('a'):
        a.unwrap()  # aタグを取り除く
    return "\n".join(soup.stripped_strings)  # 余分な空白を除去してテキストを取得

def helluva_scraper():
    print("------------helluva start----------------")
    url = "https://helluva.jp/"
    
    # Fetch the HTML page
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all date containers
    date_divs = soup.find_all('div', class_='ai1ec-date')

    if not date_divs:
        print("No date events found on the page")
        return

    current_year = datetime.now().year  # 現在の年を取得
    current_month = datetime.now().month  # 現在の月を取得

    for date_div in date_divs:
        date_link = date_div.find('a', class_='ai1ec-date-title')
        event_date_str = date_link.find('div', class_='ai1ec-day').get_text(strip=True)
        event_month_str = date_link.find('div', class_='ai1ec-month').get_text(strip=True)

        # 月の文字列を数字に変換
        event_month = int(event_month_str.replace('月', ''))  # 例: '10月' → 10

        # イベントの日付を設定
        if event_month < current_month:  # 今年の月が現在の月より小さい場合は来年に設定
            event_year = current_year + 1
        else:
            event_year = current_year

        # Combine year, month, and day to create a valid date
        event_date = datetime.strptime(f"{event_year} {event_month_str} {event_date_str}", '%Y %m月 %d')

        # Find the events within this date
        event_containers = date_div.find_all('div', class_='ai1ec-event')

        for event in event_containers:
            title = event.find('span', class_='ai1ec-event-title').get_text(strip=True)
            description = event.find('div', class_='ai1ec-event-description')
            content_body = sanitize_content(str(description)) if description else "No Description"

            # Extracting image URL from the <img> tag if present
            img_tag = description.find('img') if description else None
            image_url = img_tag['src'] if img_tag and 'src' in img_tag.attrs else None

            # Ensure that event_date is not None
            if event_date is None:
                print(f"No valid date found for event with title: {title}")
                continue  # Skip this event if date is not valid

            try:
                event, created = Helluva.objects.update_or_create(
                    date=event_date,
                    defaults={'title': title, 'content': content_body}
                )

                # 新しいイベントか、画像がまだ保存されていない場合のみ画像をダウンロード
                if created or not event.image:
                    if image_url:
                        # 相対URLをフルURLに変換
                        image_url = urljoin(url, image_url)
                        
                        image_content, image_name = save_image(image_url, title)
                        if image_content:
                            event.image.save(image_name, image_content)
                            print(f"Image saved for event '{title}'")
                else:
                    print(f"Event '{title}' updated but image already exists, skipping image download")

                if created:
                    print(f"Event '{title}' created successfully")
                else:
                    print(f"Event '{title}' updated successfully")
            except Exception as e:
                print(f"Error saving event '{title}': {e}")
    print("------------helluva end----------------")
