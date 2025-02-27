import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from django.core.files.base import ContentFile
from urllib.parse import urljoin

from ...models import Sengoku  # 適切なモデル名に変更してください

def extract_event_date(date_text):
    match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日[\s（(]*(日|月|火|水|木|金|土|日祝)[）)]*', date_text)
    if match:
        year, month, day = map(int, match.groups()[:3])
        return datetime(year, month, day)
    return None

def save_image(image_url, event_title):
    """画像のURLから画像を保存します。"""
    try:
        # Check if the URL is a valid image URL
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        ext = image_url.split('.')[-1]
        file_name = f"{event_title.replace(' ', '_')}.{ext}"
        return ContentFile(response.content), file_name
    except Exception as e:
        print(f"Error fetching image from {image_url}: {e}")
    return None, None

def sengoku_scraper():
    print("------------sengoku start----------------")
    url = "https://sengokudaitouryou.com/"
    
    # Fetch the HTML page
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    posts = soup.find_all('div', class_='post')

    if not posts:
        print("No posts found on the page")
        return

    for post in posts:
        date_header = post.find('h1', class_='title')
        date_text = date_header.get_text(strip=True) if date_header else ""
        event_date = extract_event_date(date_text)

        # Ensure that event_date is not None
        if event_date is None:
            print(f"No valid date found for post with title: {date_text}")
            continue  # Skip this post if date is not valid

        content_elements = post.find_all('p')
        # Preserve newlines by not stripping whitespace
        content = "\n".join([element.get_text(separator="\n", strip=True) for element in content_elements])  # No strip=True
        title = content.splitlines()[0] if content else "No Title"
        content_body = "\n".join(content.splitlines()[1:])  # Retain all content from the second line onward

        # Extracting image URL from the data-src attribute in figure tags
        figure_tag = post.find('figure')
        image_tag = figure_tag.find('img') if figure_tag else None
        image_url = image_tag['data-src'] if image_tag and 'data-src' in image_tag.attrs else None

        try:
            event, created = Sengoku.objects.update_or_create(
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

    print("------------sengoku end----------------")