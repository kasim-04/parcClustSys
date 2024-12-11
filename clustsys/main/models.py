from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Parcel(models.Model):
    number = models.CharField(max_length=50, unique=True, verbose_name="Номер посылки")
    address = models.CharField(max_length=255, verbose_name="Адрес")
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, verbose_name="Широта",
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, verbose_name="Долгота",
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )
    weight = models.DecimalField(
        max_digits=6, decimal_places=2, verbose_name="Вес (кг)",
        validators=[MinValueValidator(0.01)]
    )
    width = models.DecimalField(
        max_digits=6, decimal_places=2, verbose_name="Ширина коробки (м)",
        validators=[MinValueValidator(0.01)]
    )
    length = models.DecimalField(
        max_digits=6, decimal_places=2, verbose_name="Длина коробки (м)",
        validators=[MinValueValidator(0.01)]
    )
    height = models.DecimalField(
        max_digits=6, decimal_places=2, verbose_name="Высота коробки (м)",
        validators=[MinValueValidator(0.01)]
    )
    is_distributed = models.BooleanField(default=False, verbose_name="Распределена")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")

    def __str__(self):
        return self.number

    class Meta:
        verbose_name = "Посылка"
        verbose_name_plural = "Посылки"


class ParcelBatch(models.Model):
    number = models.CharField(max_length=50, unique=True, verbose_name="Номер партии")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    k = models.PositiveIntegerField(verbose_name="Количество курьеров", validators=[MinValueValidator(1)])
    max_cluster_size = models.PositiveIntegerField(verbose_name="Максимальное количество посылок в группе", validators=[MinValueValidator(1)])
    weight = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Грузоподъемность транспорта",
        validators=[MinValueValidator(0.01)]
    )
    volume = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Вместимость транспорта",
        validators=[MinValueValidator(0.01)]
    )

    def __str__(self):
        return self.number

    class Meta:
        verbose_name = "Партия посылок"
        verbose_name_plural = "Партии посылок"


class Delivery(models.Model):
    parcel_batch = models.ForeignKey(ParcelBatch, on_delete=models.CASCADE, verbose_name="Партия")
    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE, verbose_name="Посылка")
    group = models.PositiveIntegerField(verbose_name="Группа")

    def __str__(self):
        return f"{self.parcel_batch} - {self.parcel}"

    class Meta:
        verbose_name = "Доставка"
        verbose_name_plural = "Доставки"
