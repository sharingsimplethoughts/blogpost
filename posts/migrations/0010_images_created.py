# Generated by Django 2.1.5 on 2019-10-07 06:39

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0009_images'),
    ]

    operations = [
        migrations.AddField(
            model_name='images',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
