# Generated by Django 2.1.5 on 2019-11-21 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0020_pollpost_poll_end_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pollpost',
            name='poll_end_type',
            field=models.CharField(blank=True, choices=[('second', 'second'), ('minute', 'minute'), ('day', 'day'), ('week', 'week'), ('month', 'month'), ('year', 'year')], max_length=50),
        ),
    ]