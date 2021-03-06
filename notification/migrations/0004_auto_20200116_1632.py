# Generated by Django 2.1.5 on 2020-01-16 11:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0044_auto_20191217_1844'),
        ('notification', '0003_auto_20191204_1844'),
    ]

    operations = [
        migrations.AddField(
            model_name='notifications',
            name='post_id_actions',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='action_post', to='posts.Post'),
        ),
        migrations.AlterField(
            model_name='notifications',
            name='post_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='prize_winner_post', to='posts.CompetitionPost'),
        ),
    ]
