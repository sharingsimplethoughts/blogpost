# Generated by Django 2.1.5 on 2019-09-10 12:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0040_auto_20190910_1757'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='post_counts',
            new_name='post_count',
        ),
    ]
