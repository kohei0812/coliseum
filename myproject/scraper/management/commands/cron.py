from django.core.management.base import BaseCommand
from myproject.scraper.scrapes.osaka.bears_scraper import bears_scraper
from myproject.scraper.scrapes.osaka.sengoku_scraper import sengoku_scraper
from myproject.scraper.scrapes.osaka.helluva_scraper import helluva_scraper

class Command(BaseCommand):
    help = 'Scrape events from the website'

    def handle(self, *args, **kwargs):
        bears_scraper()
        sengoku_scraper()
        helluva_scraper()
        self.stdout.write(self.style.SUCCESS('Successfully scraped events.'))