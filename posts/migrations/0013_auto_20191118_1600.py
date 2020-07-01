# Generated by Django 2.1.5 on 2019-11-18 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0012_auto_20191118_1511'),
    ]

    operations = [
        migrations.RenameField(
            model_name='competitionpost',
            old_name='prize_delivery_time',
            new_name='prize_delivery_time_type',
        ),
        migrations.RemoveField(
            model_name='competitionpost',
            name='comp_image_video',
        ),
        migrations.RemoveField(
            model_name='competitionpost',
            name='prize_image_url',
        ),
        migrations.AddField(
            model_name='competitionpost',
            name='prize_delivery_time_value',
            field=models.CharField(blank=True, max_length=5),
        ),
        migrations.AlterField(
            model_name='competitionpost',
            name='countdown_time',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name='competitionpost',
            name='no_of_winners',
            field=models.CharField(blank=True, max_length=4),
        ),
        migrations.AlterField(
            model_name='competitionpost',
            name='personal_msg',
            field=models.TextField(blank=True),
        ),
    ]
