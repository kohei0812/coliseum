import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from django.core.files.base import ContentFile
from urllib.parse import urljoin

from ...models import Fuzz  # Adjust to your actual model name

def extract_event_date(date_text):
    # Matches date format as MM.DD (e.g., 10.30)
    match = re.search(r'(\d+)\.(\d+)', date_text)
    if match:
        month, day = map(int, match.groups())
        return datetime(datetime.now().year, month, day)  # Use current year
    return None

def save_image(image_url, event_title, max_length=50):
    """Download and save an image from a URL with a filename length restriction."""
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        ext = image_url.split('.')[-1]
        file_name = f"{event_title.replace(' ', '_')[:max_length]}.{ext}"
        return ContentFile(response.content), file_name
    except Exception as e:
        print(f"Error fetching image from {image_url}: {e}")
    return None, None

def fuzz_scraper():
    current_year = datetime.now().year
    url = f"https://fuzz-mikunigaoka.com/{current_year}-schedule/"

    # Fetch the HTML page
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    posts = soup.find_all('details', class_='ark-block-accordion__item')

    if not posts:
        print("No events found on the page")
        return

    for post in posts:
        # Extract date from summary and convert it to a datetime object
        date_header = post.find('summary', class_='ark-block-accordion__title')
        date_text = date_header.get_text(strip=True) if date_header else ""
        event_date = extract_event_date(date_text)

        if event_date is None:
            print(f"No valid date found for event: {date_text}")
            continue  # Skip event if date is not valid

        # Extract title and performers from label
        label_span = post.find("span", class_="ark-block-accordion__label")
        if label_span:
            lines = label_span.get_text(separator="\n").splitlines()
            title = lines[0].strip() if len(lines) > 0 else "No Title"
            performers = lines[1].strip() if len(lines) > 1 else "No Performers"
        else:
            title, performers = "No Title", "and more..."

        # Extract content from <div class="ark-block-accordion__body">
        body_div = post.find("div", class_="ark-block-accordion__body ark-keep-mt--s")
        content_elements = body_div.find_all("p") if body_div else []
        content = "\n".join([element.get_text(separator="\n", strip=True) for element in content_elements]) if content_elements else "No Content"

        # Extract image URL
        figure_tag = post.find('figure')
        image_tag = figure_tag.find('img') if figure_tag else None
        image_url = image_tag['src'] if image_tag and 'src' in image_tag.attrs else None

        try:
            # Save or update the event in the database
            event, created = Fuzz.objects.update_or_create(
                date=event_date,
                defaults={
                    'title': title,
                    'content': content,
                    'performers': performers
                }
            )

            # Save the image if the event is new or has no image
            if created or not event.image:
                if image_url:
                    # Convert relative URL to absolute
                    image_url = urljoin(url, image_url)
                    image_content, image_name = save_image(image_url, title)
                    if image_content:
                        event.image.save(image_name, image_content)
                        print(f"Image saved for event '{title}'")

            if created:
                print(f"Event '{title}' created successfully")
            else:
                print(f"Event '{title}' updated successfully")
        except Exception as e:
            print(f"Error saving event '{title}': {e}")

    print("Scraping executed")
