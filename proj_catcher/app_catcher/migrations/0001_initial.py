# Generated by Django 3.1.3 on 2020-11-19 04:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='phq9',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phq_id', models.CharField(default='0', max_length=50)),
                ('num01', models.CharField(default='0', max_length=1)),
                ('num02', models.CharField(default='0', max_length=1)),
                ('num03', models.CharField(default='0', max_length=1)),
                ('num04', models.CharField(default='0', max_length=1)),
                ('num05', models.CharField(default='0', max_length=1)),
                ('num06', models.CharField(default='0', max_length=1)),
                ('num07', models.CharField(default='0', max_length=1)),
                ('num08', models.CharField(default='0', max_length=1)),
                ('num09', models.CharField(default='0', max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='users',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(max_length=50)),
                ('datatest', models.CharField(max_length=50)),
            ],
        ),
    ]