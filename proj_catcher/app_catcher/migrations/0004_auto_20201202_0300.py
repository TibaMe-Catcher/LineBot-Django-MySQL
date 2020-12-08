# Generated by Django 3.1.3 on 2020-12-01 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_catcher', '0003_users'),
    ]

    operations = [
        migrations.AddField(
            model_name='diary',
            name='text_score',
            field=models.FloatField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='picture',
            name='picture_score',
            field=models.FloatField(blank=True, default=None, null=True),
        ),
    ]