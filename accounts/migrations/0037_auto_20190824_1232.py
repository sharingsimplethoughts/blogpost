# Generated by Django 2.1.5 on 2019-08-24 07:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0036_profileviewscountrecord_profileviewsrecoard_removefromsuggestionsrecord'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='removefromsuggestionsrecord',
            name='remove_by',
        ),
        migrations.RemoveField(
            model_name='removefromsuggestionsrecord',
            name='remove_to',
        ),
        migrations.DeleteModel(
            name='RemoveFromSuggestionsRecord',
        ),
    ]
