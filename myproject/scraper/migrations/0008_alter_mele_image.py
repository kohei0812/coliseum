# Generated by Django 5.1.2 on 2024-10-30 12:50

import scraper.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0007_mele'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mele',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=scraper.models.get_image_upload_mele),
        ),
    ]