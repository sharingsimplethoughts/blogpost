# Generated by Django 2.1.5 on 2019-08-23 06:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0035_auto_20190809_1646'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfileViewsCountRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('profile_blog_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile_blog_count_by', to=settings.AUTH_USER_MODEL)),
                ('profile_blog_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile_blog_count_to', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProfileViewsRecoard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('profile_blog_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile_blog_by', to=settings.AUTH_USER_MODEL)),
                ('profile_blog_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile_blog_to', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RemoveFromSuggestionsRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('remove_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='remove_by', to=settings.AUTH_USER_MODEL)),
                ('remove_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='remove_to', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
