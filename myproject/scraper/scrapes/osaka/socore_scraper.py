import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from django.core.files.base import ContentFile
from urllib.parse import urljoin
from ...models import Socore  # Adjust to your model name

def extract_event_date(year, month, day):
    """Create a datetime object from year, month, and day."""
    return datetime(year, month, day)

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

def socore_scraper():
    now = datetime.now()
    
    # Determine the target URL based on the current month
    if now.month == 12:
        target_month = 1
        target_year = now.year + 1
    else:
        target_month = now.month + 1
        target_year = now.year

    url = f"https://socorefactory.com/schedule/{target_year}/{target_month:02d}/"

    # Fetch the HTML page
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    schedule_divs = soup.find_all('div', class_='schedule')

    if not schedule_divs:
        print("No events found on the page")
        return

    for schedule_div in schedule_divs:
        # Extract the day
        day_elem = schedule_div.find('p', class_='days')
        day_text = day_elem.get_text(strip=True) if day_elem else ""
        
        # Convert day_text to an integer
        if not day_text.isdigit():
            print(f"Invalid day found for event: {schedule_div}")
            continue
        day = int(day_text)

        # Extract the title and remove everything before the "|"
        title_elem = schedule_div.find('h3')
        title_text = title_elem.get_text(strip=True) if title_elem else "No Title"
        title = title_text.split('|', 1)[-1].strip()  # Keep only the part after the "|"

        # Extract the performers from <p class="act">
        act_elem = schedule_div.find('p', class_='act')
        performers_text = act_elem.get_text(separator="\n", strip=True) if act_elem else "No Performers"

        # Extract the content from the following <p> elements (e.g., start time, ticket prices)
        content_elem = act_elem.find_next_sibling('p')  # Find the next <p> for content
        content_text = content_elem.get_text(separator="\n", strip=True) if content_elem else "No Content"

        # Extract the image URL
        image_tag = schedule_div.find('img', class_='wp-post-image')
        image_url = image_tag['data-lazy-src'] if image_tag and 'data-lazy-src' in image_tag.attrs else None

        # Create the event date using the target year, target month, and extracted day
        event_date = extract_event_date(target_year, target_month, day)

        if event_date is None:
            print(f"No valid date found for event: {title}")
            continue

        try:
            # Save or update the event in the database
            event, created = Socore.objects.update_or_create(
                date=event_date,
                defaults={
                    'title': title,
                    'content': content_text,
                    'performers': performers_text
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

# Call the scraper
# socore_scraper()
