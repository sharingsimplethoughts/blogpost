# Generated by Django 2.1.5 on 2019-10-03 11:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chat', '0002_auto_20190829_1559'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupMemberLists',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_id', models.CharField(max_length=500)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
