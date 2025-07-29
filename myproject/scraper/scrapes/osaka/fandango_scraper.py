import requests
from bs4 import BeautifulSoup
from datetime import datetime
from django.core.files.base import ContentFile
from ...models import Fandango
import re
import logging

# ロガー設定
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def download_image_from_url(image_url):
    """画像のURLからダウンロード"""
    try:
        logger.debug(f"Downloading image from: {image_url}")
        image_response = requests.get(image_url, stream=True)
        image_response.raise_for_status()
        return image_response.content
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download image from {image_url}: {e}")
        return None

def fullwidth_to_halfwidth(text):
    """全角数字を半角数字に変換"""
    translation_table = str.maketrans("０１２３４５６７８９", "0123456789")
    return text.translate(translation_table)

def fandango_scraper():
    print("------------ fandango start ----------------")

    base_url = "https://www.fandango-japan.com"
    response = requests.get(base_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # 現在の月と次の月を取得
    now = datetime.now()
    next_month = now.month + 1 if now.month < 12 else 1

    # 次の月のスケジュールページのリンクを取得
    next_month_link = None
    nav_items = soup.select('.global-nav__list .global-nav__item a')

    for item in nav_items:
        link_text = fullwidth_to_halfwidth(item.text).strip()
        if f"SCHEDULE（{next_month}月）" in link_text:
            next_month_link = item['href']
            break

    if not next_month_link:
        logger.error(f"SCHEDULE for month {next_month} not found!")
        return

    # 絶対URLに変換
    schedule_url = requests.compat.urljoin(base_url, next_month_link)
    logger.info(f"Scraping schedule page: {schedule_url}")

    response = requests.get(schedule_url)
    response.raise_for_status()
    soup_next = BeautifulSoup(response.text, 'html.parser')

    # イベント情報の取得
    events = []
    event_blocks = soup_next.select('.page__main .block__outer')

    for block in event_blocks:
        p_tags = block.select('.block-txt p')
        if len(p_tags) < 4:
            continue

        raw_date = p_tags[0].text.strip()  # 日付
        title = p_tags[1].text.strip()  # タイトル
        performers = p_tags[3].text.strip()  # 出演者
        content = "\n".join([p.text.strip() for p in p_tags[4:]])  # 内容

        # 日付フォーマットを変換
        match = re.match(r'(\d{4})\.(\d{1,2})/(\d{1,2})', raw_date)
        if match:
            year, month, day = match.groups()
            event_date = datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d")
        else:
            logger.error(f"Failed to parse date: {raw_date}")
            continue

        # 画像の取得
        image_elem = block.select_one('.block-type--image img')
        image_url = None
        if image_elem:
            image_url = requests.compat.urljoin(schedule_url, image_elem['src'])

        # イベント情報をリストに追加
        event = {
            'date': event_date,
            'title': title,
            'performers': performers,
            'content': content,
            'image': image_url
        }
        events.append(event)

    # データベースへの保存
    for event in events:
        try:
            event_instance, created = Fandango.objects.update_or_create(
                date=event['date'],
                defaults={
                    'title': event['title'],
                    'performers': event['performers'],
                    'content': event['content'],
                }
            )

            # 画像の保存処理
            if event['image']:
                image_content = download_image_from_url(event['image'])
                if image_content:
                    ext = event['image'].split('.')[-1]
                    image_name = f"{event_instance.title.replace(' ', '_')}.{ext}"
                    event_instance.image.save(image_name, ContentFile(image_content))
                    logger.info(f"Image saved for event '{event['title']}'")
                else:
                    logger.error(f"Failed to download image for '{event['title']}'")

            if created:
                logger.info(f"Event '{event['title']}' created successfully")
            else:
                logger.info(f"Event '{event['title']}' updated successfully")

        except Exception as e:
            logger.error(f"Error saving event '{event['title']}': {e}")

    print("------------ fandango end ----------------")
