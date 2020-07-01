# Generated by Django 2.1.5 on 2019-07-18 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0029_user_is_private_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='message_privacy',
            field=models.CharField(choices=[('1', 'only me'), ('2', 'viewing'), ('3', 'public')], default='1', max_length=20),
        ),
        migrations.AddField(
            model_name='user',
            name='post_privacy',
            field=models.CharField(choices=[('1', 'only me'), ('2', 'viewing'), ('3', 'public')], default='1', max_length=20),
        ),
    ]
