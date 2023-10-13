import json

import requests

from settings import config


def get_city_coord(city):
    payload = {'apikey': config.api_geo, 'geocode': city, 'format': 'json'}
    r = requests.get('https://geocode-maps.yandex.ru/1.x', params=payload)
    # url = f'https://geocode-maps.yandex.ru/1.x?apikey=62a7fe6e-f973-466a-a0e3-29eae770b8a6&geocode=Бобруйск'
    # r = requests.get(url=url, headers={
    #     'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
    #     })
    #return r.text
    geo = json.loads(r.text)
    try:
        return geo['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
    except KeyError as ex:
        return r.text
        return f"KeyError {ex}"
print(get_city_coord('Бобруйск'))

def get_weather(city):
    try:
        coord = get_city_coord(city)
    except KeyError:
        coord = ['37.6176', '55.7558']
    payload = {'lat':coord[1], 'lon':coord[0], 'lang': 'ru_RU'}
    r = requests.get('https://api.weather.yandex.ru/v2/informers', 
                        params=payload, headers={
                            'X-Yandex-API-Key': config.api_key_weather
                        })
    return r.json()

#print(get_weather('Бобруйск'))
    