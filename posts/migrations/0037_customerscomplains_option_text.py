# Generated by Django 2.1.5 on 2019-12-05 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0036_competitionwinnersprizedeliverystatus_customerscomplains'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerscomplains',
            name='option_text',
            field=models.TextField(default='ww'),
            preserve_default=False,
        ),
    ]
