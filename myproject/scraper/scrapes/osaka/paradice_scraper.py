import os
import re
import requests
import logging
from bs4 import BeautifulSoup
from django.utils import timezone
from django.core.files.base import ContentFile
from urllib.parse import urljoin
from datetime import datetime
from ...models import Paradice

URL = "https://para-dice.net/"

# ロギング設定
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def extract_event_date(date_text, year_month_text):
    """thタグの<p>タグから日付を取得し、yearと結合してdatetimeに変換"""
    match = re.search(r'(\d{4})/(\d{1,2})', year_month_text)
    if not match:
        logging.warning(f"Skipping - Invalid year/month format: {year_month_text}")
        return None

    year, month = map(int, match.groups())

    # "2/1" のような日付を抽出
    day_match = re.search(r'(\d{1,2})/(\d{1,2})', date_text)
    if not day_match:
        logging.warning(f"Skipping - Invalid date format: {date_text}")
        return None

    extracted_month, day = map(int, day_match.groups())

    # 月の整合性チェック
    if extracted_month != month:
        logging.warning(f"Month mismatch: Expected {month}, but got {extracted_month}")
        return None

    return datetime(year, month, day)

def paradice_scraper():
    logging.info("------------ Paradice Scraper Start ----------------")

    try:
        response = requests.get(URL)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching URL: {e}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    schedule_div = soup.find("div", id="Schedule")
    if not schedule_div:
        logging.warning("No Schedule div found!")
        return

    success_count, failure_count = 0, 0

    # 各月ごとの `eachMonth` div を取得
    month_blocks = schedule_div.find_all("div", class_="eachMonth")
    
    for month_block in month_blocks:
        # 年月取得
        year_month_tag = month_block.find("h3", class_="yearDate")
        year_month_text = year_month_tag.get_text(strip=True) if year_month_tag else ""
        
        # その月の `table[summary="スケジュール"]` を取得
        schedule_table = month_block.find("table", summary="スケジュール")
        if not schedule_table:
            logging.warning(f"No schedule table found for {year_month_text}")
            continue

        # テーブル内の `tr` を取得
        rows = schedule_table.find_all("tr")

        for row in rows:
            try:
                th_tag = row.find("th")
                if not th_tag:
                    continue

                date_p_tags = th_tag.find_all("p")
                if not date_p_tags:
                    logging.warning("No <p> found in <th>")
                    continue

                date_text = date_p_tags[0].get_text(strip=True)
                event_date = extract_event_date(date_text, year_month_text)
                if not event_date:
                    continue

                # タイトル取得
                title_tag = row.find("p", class_="style5")
                title = title_tag.get_text(strip=True) if title_tag else "No Title"

                # `td` 内の `<p>` で `style` がなく、`img` を含まないものを `content` に統合
                td_tag = row.find("td")
                if td_tag:
                    content_p_tags = [
                        p.get_text(strip=True)
                        for p in td_tag.find_all("p")
                        if not p.has_attr("class") and not p.find("img")
                    ]
                    content = "\n".join(content_p_tags)
                else:
                    content = ""

                # 画像取得
                image_tag = row.find("img")
                image_url = image_tag["src"] if image_tag else None
                if image_url and not image_url.startswith(("http://", "https://")):
                    image_url = urljoin(URL, image_url.lstrip("/"))

                # データ保存
                event, created = Paradice.objects.update_or_create(
                    date=event_date,
                    defaults={
                        "title": title,
                        "content": content,
                        "performers": "",
                    }
                )

                # 画像保存（重複を防ぐ）
                if image_url:
                    if event.image and event.image.name:
                        logging.info(f"Image already exists for {title}, skipping download.")
                    else:
                        try:
                            image_response = requests.get(image_url)
                            image_response.raise_for_status()
                            image_filename = os.path.basename(image_url)
                            event.image.save(image_filename, ContentFile(image_response.content))
                            logging.info(f"Image saved for {title}")
                        except requests.exceptions.RequestException as e:
                            logging.error(f"Error downloading image: {e}")

                if created:
                    logging.info(f"Event '{title}' created successfully.")
                    success_count += 1
                else:
                    logging.info(f"Event '{title}' updated successfully.")

            except Exception as e:
                logging.error(f"Error processing event: {e}")
                logging.debug(row.prettify())
                failure_count += 1

    logging.info(f"Scraping completed! Success: {success_count}, Failures: {failure_count}")
    logging.info("------------ Paradice Scraper End ----------------")
