# Generated by Django 3.0.5 on 2020-05-07 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feeds', '0002_feed_subscribers'),
    ]

    operations = [
        migrations.AddField(
            model_name='feed',
            name='logo',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='feed',
            name='subtitle',
            field=models.CharField(max_length=1000, null=True),
        ),
    ]
