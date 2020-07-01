# Generated by Django 2.1.5 on 2019-06-20 13:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0015_auto_20190620_1645'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userinterests',
            name='activity',
        ),
        migrations.RemoveField(
            model_name='userinterests',
            name='games',
        ),
        migrations.RemoveField(
            model_name='userinterests',
            name='hobbies',
        ),
        migrations.RemoveField(
            model_name='userinterests',
            name='interested_in',
        ),
        migrations.RemoveField(
            model_name='userinterests',
            name='movies',
        ),
        migrations.RemoveField(
            model_name='userinterests',
            name='music',
        ),
        migrations.AddField(
            model_name='userinterests',
            name='interest',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userinterests',
            name='interest_type',
            field=models.CharField(choices=[('1', 'activities'), ('2', 'hobbies'), ('3', 'music'), ('4', 'movies'), ('5', 'tv-shows'), ('6', 'games')], default='', max_length=5),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userinterests',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_interest', to=settings.AUTH_USER_MODEL),
        ),
    ]
