# Generated by Django 5.1.2 on 2024-10-31 13:52

import scraper.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0012_king'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fandango',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('performers', models.TextField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to=scraper.models.get_image_upload_fandango)),
            ],
        ),
    ]
