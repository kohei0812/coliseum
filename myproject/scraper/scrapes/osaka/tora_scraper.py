import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from django.core.files.base import ContentFile
from urllib.parse import urljoin
from ...models import Tora  # Adjust to your actual model name

def extract_event_date(date_text):
    # Matches date format as YYYY MM/DD (e.g., 2024 11/01)
    match = re.search(r'(\d{4})\s(\d{1,2})/(\d{1,2})', date_text)
    if match:
        year, month, day = map(int, match.groups())
        return datetime(year, month, day)  # Use extracted year, month, and day
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

def tora_scraper():
    url = "https://live-tora.com/live-schedule-next-month"
    
    # Fetch the HTML page
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    posts = soup.find_all('div', class_='getPost')

    if not posts:
        print("No events found on the page")
        return

    for post in posts:
        # Extract date from the link text
        link = post.find('h4', class_='getPostTitle').find('a')
        if link:
            date_text = link.get_text(strip=True)
            event_date = extract_event_date(date_text)

            if event_date is None:
                print(f"No valid date found for event: {date_text}")
                continue  # Skip event if date is not valid

            # Extract title (removing the date part)
            title = None

            # Check if the date_text contains the brackets
            if '［' in date_text and '］' in date_text:
                try:
                    title = date_text.split('［')[1].split('］')[0].strip()  # Extract title from brackets
                except IndexError:
                    print(f"Error extracting title from {date_text}: brackets format incorrect")
                    continue  # Skip event if title extraction fails
            else:
                # Handle cases where brackets are not found, or use a fallback method
                title = date_text.strip()

            # Extract content from getPostContent
            content_div = post.find("div", class_="getPostContent")
            content = content_div.get_text(separator="\n", strip=True) if content_div else "No Content"

            # Remove unnecessary spaces
            content = content.replace(" ", "\n")

            # Extract image URL
            img_tag = post.find('img')
            image_url = img_tag['src'] if img_tag and 'src' in img_tag.attrs else None

            try:
                # Save or update the event in the database
                event, created = Tora.objects.update_or_create(
                    date=event_date,
                    defaults={
                        'title': title,
                        'content': content,
                        # 'performers' is removed from defaults
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
