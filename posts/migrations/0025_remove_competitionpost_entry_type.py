# Generated by Django 2.1.5 on 2019-11-22 11:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0024_competitionpost_competition_end_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='competitionpost',
            name='entry_type',
        ),
    ]
