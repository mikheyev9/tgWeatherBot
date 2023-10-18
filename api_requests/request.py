import json

import requests

from settings import config


def get_city_coord(city):
    payload = {'apikey': config.api_geo, 'geocode': city, 'format': 'json'}
    r = requests.get('https://geocode-maps.yandex.ru/1.x', params=payload)
    geo = json.loads(r.text)
    try:
        return geo['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
    except KeyError as ex:
        return f"KeyError {ex}"


def get_weather(city):
    try:
        coord = get_city_coord(city)
    except KeyError:
        coord = ['37.6176', '55.7558']
    payload = {'lat':coord[0], 'lon':coord[1], 'lang': 'ru_RU'}
    r = requests.get('https://api.weather.yandex.ru/v2/informers', 
                        params=payload, headers={
                            'X-Yandex-API-Key': config.api_key_weather
                        })
    return r.json()

    