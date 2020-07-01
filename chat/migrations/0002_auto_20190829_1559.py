# Generated by Django 2.1.5 on 2019-08-29 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mediafile',
            name='file',
            field=models.FileField(blank=True, max_length=1000, null=True, upload_to='chat_media/'),
        ),
        migrations.AlterField(
            model_name='mediafile',
            name='thumb',
            field=models.FileField(blank=True, max_length=1000, null=True, upload_to='video_thumb/'),
        ),
    ]
