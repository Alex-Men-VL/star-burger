# Generated by Django 3.2 on 2022-01-18 17:46
import requests
from django.conf import settings
from django.db import migrations


def fetch_coordinates(address):
    url = 'https://geocode-maps.yandex.ru/1.x'
    apikey = settings.YANDEX_API_KEY
    params = {
        'geocode': address,
        'apikey': apikey,
        'format': 'json',
    }
    response = requests.get(url, params=params)
    response.raise_for_status()

    found_places = response.json()['response'][
        'GeoObjectCollection'
    ]['featureMember']

    if not found_places:
        return None

    most_relevant_place = found_places[0]
    lon, lat = most_relevant_place['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def add_coordinates(apps, schema_editor):
    Coordinate = apps.get_model('coordinates', 'Coordinate')
    Order = apps.get_model('foodcartapp', 'Order')
    Restaurant = apps.get_model('foodcartapp', 'Restaurant')

    for item in [*Order.objects.all(), *Restaurant.objects.all()]:
        coordinates = {}
        try:
            lon, lat = fetch_coordinates(item.address)
        except Exception:
            pass
        else:
            coordinates['lon'] = lon
            coordinates['lat'] = lat
            coordinates['status'] = 'D'
        Coordinate.objects.create(address=item.address, **coordinates)


class Migration(migrations.Migration):

    dependencies = [
        ('coordinates', '0002_coordinate_request_date'),
    ]

    operations = [
        migrations.RunPython(add_coordinates),
    ]