from django.db import models
from django.utils import timezone


class Coordinate(models.Model):
    DEFINED = 'D'
    NOT_DEFINED = 'ND'
    COORDINATE_STATUS_CHOICE = [
        (DEFINED, 'определены'),
        (NOT_DEFINED, 'не определены')
    ]
    address = models.CharField(
        'адрес',
        max_length=100
    )
    lon = models.FloatField(
        'долгота',
        null=True,
        blank=True,
    )
    lat = models.FloatField(
        'широта',
        null=True,
        blank=True,
    )
    status = models.CharField(
        'статус координат',
        max_length=13,
        choices=COORDINATE_STATUS_CHOICE,
        default=NOT_DEFINED
    )
    request_date = models.DateTimeField(
        'дата запроса к геокодеру',
        default=timezone.now
    )

    class Meta:
        verbose_name = 'координаты'
        verbose_name_plural = 'координаты'

    def __str__(self):
        return f'{self.address} ({self.lon} {self.lat})'
