import requests
from bs4 import BeautifulSoup
from datetime import datetime
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from ...models import King  # Djangoモデルのインポート
import logging

def generate_url():
    now = datetime.now()
    if now.month == 12:
        year, month = now.year + 1, 1
    else:
        year, month = now.year, now.month + 1
    return year, month, f"http://king-cobra.net/schedule/{year}_{month:02}.html"

def scrape_main_page():
    url = 'http://king-cobra.net/main.html'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    events = []
    
    # Find the table containing events
    event_table = soup.find('table', width='1252')
    if not event_table:
        logging.warning("Event table not found.")
        return
    
    # Iterate through each row in the event table
    for row in event_table.find_all('tr'):
        for cell in row.find_all('td'):
            # Get the image and the associated text
            img_tag = cell.find('img')
            date_paragraph = cell.find_all('p')[1]  # The second <p> contains the date
            title_paragraph = cell.find_all('p')[2]  # The third <p> contains the title
            
            if img_tag and date_paragraph and title_paragraph:
                img_src = img_tag['src']
                date_text = date_paragraph.get_text(strip=True)
                title_text = title_paragraph.get_text(strip=True)
                
                # Extracting date
                try:
                    month_day = date_text.split('（')[0].strip()  # Clean up whitespace
                    month, day = month_day.split('/')
                    year = datetime.now().year  # Assuming the current year for scraping
                    date_str = f"{year}-{int(month):02}-{int(day):02}"
                    event_date = datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError as e:
                    logging.error(f"Date parsing error for '{date_text}': {e}")
                    continue  # Skip this entry if date parsing fails
                
                # Create event object
                event = {
                    'date': event_date,
                    'title': title_text,
                    'content': '',  # Placeholder for content
                    'performers': '',  # Placeholder for performers
                    'image': img_src,
                }
                events.append(event)
            else:
                logging.warning("Missing image, date, or title in the event cell.")

    # Process the collected events as needed (e.g., save to database)
    for event in events:
        print(event)  # Replace this with your database save logic

def king_scraper():
    year, month, url = generate_url()
    try:
        response = requests.get(url)
        response.encoding = 'shift_jis'
        soup = BeautifulSoup(response.text, 'html.parser')

        for event_row in soup.find_all('tr'):
            try:
                date_cell = event_row.find('td', width="83")
                if not date_cell:
                    continue
                
                date_text = date_cell.get_text(strip=True)
                if not date_text:
                    continue  # Skip if date is empty

                if '月' in date_text and '日' in date_text:
                    clean_date_text = date_text.split('-')[0]
                    clean_date_text = clean_date_text.replace('月', '-').replace('日', '').strip()
                    date_str = f"{year}-{clean_date_text.zfill(2)}"
                    event_date = datetime.strptime(date_str, "%Y-%m-%d")
                else:
                    continue  # Skip if date format is invalid
                
                title_cell = date_cell.find_next('td')
                title = title_cell.get_text(strip=True).replace("『", "").replace("』", "")
                if not title:
                    print(f"Warning: Empty title for date {event_date}.")
                    continue  # Skip if title is empty
                
                performers_cell = title_cell.find_next('td')
                performers = performers_cell.get_text(separator="\n", strip=True).replace("■出演者", "")
                
                open_start_cell = performers_cell.find_next('td')
                open_start = open_start_cell.get_text(separator=" ", strip=True)
                
                ticket_cell = open_start_cell.find_next('td')
                ticket = ticket_cell.get_text(separator=" ", strip=True).replace("・", "")
                
                content = f"{open_start}\n{ticket}"
                
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

    except Exception as outer_exception:
        print(f"Failed to scrape data from {url}: {outer_exception}")

# スクリプトの実行
# if __name__ == "__main__":
#     scrape_main_page()  # メインページのスクレイピングを実行
#     king_scraper()      # イベント情報のスクレイピングを実行
