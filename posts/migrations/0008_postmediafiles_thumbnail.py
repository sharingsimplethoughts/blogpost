# Generated by Django 2.1.5 on 2019-09-30 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_auto_20190930_1108'),
    ]

    operations = [
        migrations.AddField(
            model_name='postmediafiles',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to='video_thumbnail'),
        ),
    ]
