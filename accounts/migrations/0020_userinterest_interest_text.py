# Generated by Django 2.1.5 on 2019-06-26 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0019_userinterest'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinterest',
            name='interest_text',
            field=models.TextField(blank=True),
        ),
    ]