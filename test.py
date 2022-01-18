import requests
from django.conf import settings


def fetch_coordinates(apikey, address):
    url = 'https://geocode-maps.yandex.ru/1.x'
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
    print(lon, lat)


if __name__ == '__main__':
    # apikey = settings.YANDEX_API_KEY
    apikey = 'a71fc090-54e9-439a-9a79-4c5e37db5dfc'
    address = 'Москва, ул. Льва Толстого, 16'
    fetch_coordinates(apikey, address)
