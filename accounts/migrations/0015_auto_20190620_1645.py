# Generated by Django 2.1.5 on 2019-06-20 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_auto_20190620_1643'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usercontactinfo',
            name='ethnicity',
        ),
        migrations.AddField(
            model_name='usercontactinfo',
            name='ethnicity',
            field=models.ManyToManyField(blank=True, to='accounts.Ethnicity'),
        ),
    ]
