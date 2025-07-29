import os
import re
import requests
import logging
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from django.core.files.base import ContentFile
from ...models import Hardrain  # モデル名変更済み
from bs4 import NavigableString, Tag

# ロギング設定
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_target_url():
    today = datetime.today()
    if today.month == 12:
        target = datetime(today.year + 1, 1, 1)
    else:
        target = datetime(today.year, today.month + 1, 1)
    return f"http://hardrain-web.net/schedule{target.strftime('%y%m')}.html", target.year, target.month


def extract_date(text, year):
    """例: '2025年4月2日(水)' → datetime.date(2025, 4, 2)"""
    match = re.search(r'(\d{1,2})月(\d{1,2})日', text)
    if match:
        month, day = map(int, match.groups())
        return datetime(year, month, day)
    return None

def hardrain_scraper():
    logging.info("------------ Hardrain Scraper Start ----------------")

    url, year, month = get_target_url()
    try:
        response = requests.get(url)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching URL: {e}")
        return

    soup = BeautifulSoup(response.content, "html.parser")
    date_divs = soup.find_all("div", class_=re.compile("date|datesat|datesun|holiday"))

    success, fail = 0, 0
    for date_div in date_divs:
        try:
            date_text = date_div.get_text(strip=True)
            event_date = extract_date(date_text, year)
            if not event_date:
                logging.warning(f"Invalid date: {date_text}")
                continue

            comment_div = date_div.find_next_sibling("div", class_="comment")
            if not comment_div:
                logging.warning("No comment block found.")
                continue

            # <br>区切りでの解析
            lines = []
            current_line = ""
            for content in comment_div.contents:
                if isinstance(content, NavigableString):
                    current_line += str(content).strip()
                elif isinstance(content, Tag) and content.name == "br":
                    lines.append(current_line.strip())
                    current_line = ""
                else:
                    current_line += content.get_text(strip=True)
            if current_line.strip():
                lines.append(current_line.strip())

            # 空行も含めて、明確に<br><br>の位置を検出
            clean_lines = [line for line in lines]

            title = clean_lines[0] if clean_lines else "No Title"

            # performers: titleの次から最初の空行まで
            performers = []
            content_lines = []

            for line in clean_lines[1:]:
                if line == "":
                    # 空行が来たら content に切り替え
                    break
                performers.append(line)

            performer_count = len(performers)
            content_lines = clean_lines[1 + performer_count + 1 :]  # 空行の分+1

            performers_text = "\n".join(performers).strip()
            content_text = "\n".join(content_lines).strip()

            event, created = Hardrain.objects.update_or_create(
                date=event_date,
                defaults={
                    "title": title,
                    "performers": performers_text,
                    "content": content_text,
                }
            )

            logging.info(f"{'Created' if created else 'Updated'} event: {title}")
            success += 1
        except Exception as e:
            logging.error(f"Error processing event: {e}")
            fail += 1

    logging.info(f"Done! Success: {success}, Failed: {fail}")
    logging.info("------------ Hardrain Scraper End ----------------")