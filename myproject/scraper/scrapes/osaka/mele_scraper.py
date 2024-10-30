import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from django.core.files.base import ContentFile
from urllib.parse import urljoin

from ...models import Mele  # Adjust to your model name

def extract_event_date(date_text):
    print(f"Raw date text: {date_text}")  # Debug print to check date text
    # Check if date_text is bytes and decode if necessary
    if isinstance(date_text, bytes):
        date_text = date_text.decode('utf-8', errors='ignore')

    match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', date_text)
    if match:
        year, month, day = map(int, match.groups())
        return datetime(year, month, day)
    return None

def save_image(image_url, event_title):
    """Download and save an image from a URL."""
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        ext = image_url.split('.')[-1]
        file_name = f"{event_title.replace(' ', '_')}.{ext}"
        return ContentFile(response.content), file_name
    except Exception as e:
        print(f"Error fetching image from {image_url}: {e}")
    return None, None

def mele_scraper():
    now = datetime.now()
    if now.month == 12:
        # If it's December, set the next month to January of the next year
        next_month = datetime(now.year + 1, 1, 1)
    else:
        # Otherwise, get the next month in the current year
        next_month = now.replace(day=1, month=(now.month % 12) + 1)

    url = f"https://namba-mele.com/schedule/{next_month.strftime('%Y%m')}.html"

    response = requests.get(url)
    response.encoding = 'utf-8'  # Ensure UTF-8 encoding
    soup = BeautifulSoup(response.text, 'html.parser')
    event_sections = soup.find_all("div", class_="sche_wrap")

    if not event_sections:
        print("No events found on the page")
        return

    for event_section in event_sections:
        # Extract title and date information
        title_date = event_section.find("p", class_="title")
        title_date_text = title_date.get_text(strip=True) if title_date else ""
        
        # Extract the date from the title text
        event_date = extract_event_date(title_date_text)

        # Extract title, ensuring the format is maintained
        title_match = re.search(r'「(.*?)」', title_date_text)
        title = title_match.group(1) if title_match else "No Title"

        # Ensure valid date
        if event_date is None:
            print(f"No valid date found for event: {title_date_text}")
            continue

        # Extract additional details like open/start times
        details = event_section.find("p", class_="date")
        content = details.get_text(separator="\n",strip=True) if details else "No Details"

        # Extract performers
        performers_section = event_section.find("p", class_="text")
        performers = performers_section.get_text(separator="\n", strip=True) if performers_section else "No Performers"

        # Extract image
        image_div = event_section.find("div", class_="mb5")
        image_tag = image_div.find("img") if image_div else None
        image_url = image_tag['src'] if image_tag and 'src' in image_tag.attrs else None

        try:
            # Save event in the database
            event, created = Mele.objects.update_or_create(
                date=event_date,
                defaults={
                    'title': title,
                    'content': content,
                    'performers': performers,
                }
            )

            # Download and save the image if new or missing
            if created or not event.image:
                if image_url:
                    image_url = urljoin(url, image_url)
                    image_content, image_name = save_image(image_url, title)
                    if image_content:
                        event.image.save(image_name, image_content)
                        print(f"Image saved for event '{title}'")
            else:
                print(f"Event '{title}' updated but image already exists")

            print(f"Event '{title}' {'created' if created else 'updated'} successfully")
        except Exception as e:
            print(f"Error saving event '{title}': {e}")

# Call the scraper
# namba_mele_scraper()
