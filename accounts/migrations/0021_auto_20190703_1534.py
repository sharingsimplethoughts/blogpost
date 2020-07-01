# Generated by Django 2.1.5 on 2019-07-03 10:04

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0020_userinterest_interest_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='viewers',
            field=models.ManyToManyField(blank=True, related_name='_user_viewers_+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='user',
            name='viewing',
            field=models.ManyToManyField(blank=True, related_name='_user_viewing_+', to=settings.AUTH_USER_MODEL),
        ),
    ]