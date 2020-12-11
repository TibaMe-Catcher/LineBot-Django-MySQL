# Generated by Django 3.1.3 on 2020-12-08 13:47

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
                ('text_score', models.FloatField(blank=True, default=None, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('diary_uid', models.CharField(default=None, max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Picture',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('picture_id', models.CharField(default=None, max_length=50)),
                ('picture_score', models.FloatField(blank=True, default=None, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('picture_uid', models.CharField(default=None, max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Surprise',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sur_id', models.CharField(default=None, max_length=15)),
                ('category', models.TextField(blank=True, default=None)),
                ('mood', models.TextField(blank=True, default=None)),
                ('title', models.TextField(blank=True, default=None)),
                ('content', models.TextField(blank=True, default=None, max_length=300)),
            ],
        ),
    ]
