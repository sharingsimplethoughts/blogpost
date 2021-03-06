# Generated by Django 2.1.5 on 2019-11-20 10:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0017_voteapoll'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompetitionEnteredUsers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('entered_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entered_user', to=settings.AUTH_USER_MODEL)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entry_comp_post', to='posts.Post')),
            ],
        ),
    ]
