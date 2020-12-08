# Generated by Django 3.1.3 on 2020-11-29 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Diary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('diary_id', models.CharField(default=None, max_length=15)),
                ('text', models.TextField(blank=True, default=None)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('diary_uid', models.CharField(default=None, max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Picture',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('picture_id', models.CharField(default=None, max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('picture_uid', models.CharField(default=None, max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('phq_score', models.CharField(max_length=50)),
            ],
        ),
    ]
