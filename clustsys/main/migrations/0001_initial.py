# Generated by Django 5.1.3 on 2024-11-21 13:59

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Parcel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=50, unique=True, verbose_name='Номер посылки')),
                ('address', models.CharField(max_length=255, verbose_name='Адрес')),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9, verbose_name='Широта')),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9, verbose_name='Долгота')),
                ('weight', models.DecimalField(decimal_places=2, max_digits=6, verbose_name='Вес')),
                ('width', models.DecimalField(decimal_places=2, max_digits=6, verbose_name='Ширина коробки')),
                ('length', models.DecimalField(decimal_places=2, max_digits=6, verbose_name='Длина коробки')),
                ('height', models.DecimalField(decimal_places=2, max_digits=6, verbose_name='Высота коробки')),
                ('is_distributed', models.BooleanField(default=False, verbose_name='Распределена')),
            ],
            options={
                'verbose_name': 'Посылка',
                'verbose_name_plural': 'Посылки',
            },
        ),
        migrations.CreateModel(
            name='ParcelBatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=50, unique=True, verbose_name='Номер партии')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Партия посылок',
                'verbose_name_plural': 'Партии посылок',
            },
        ),
        migrations.CreateModel(
            name='Delivery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.PositiveIntegerField(verbose_name='Группа')),
                ('parcel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.parcel', verbose_name='Посылка')),
                ('parcel_batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.parcelbatch', verbose_name='Партия')),
            ],
            options={
                'verbose_name': 'Доставка',
                'verbose_name_plural': 'Доставки',
            },
        ),
    ]
