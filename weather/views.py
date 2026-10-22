
import requests
from django.shortcuts import render

API_KEY = '0ed8282745c4e1be7bfd5b609f6530f4'
API_URL = 'https://api.openweathermap.org/data/2.5/weather'

DEFAULT_CITIES = [
    'Rostov-on-Don',
    'Moscow',
    'Saint Petersburg',
]


def get_weather(city):
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric',
        'lang': 'ru',
    }

    response = requests.get(API_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    return {
        'city': data['name'],
        'country': data['sys']['country'],
        'temperature': round(data['main']['temp']),
        'feels_like': round(data['main']['feels_like']),
        'description': data['weather'][0]['description'],
        'icon': data['weather'][0]['icon'],
        'wind_speed': data['wind']['speed'],
        'pressure': data['main']['pressure'],
        'humidity': data['main']['humidity'],
    }


def index(request):
    city_input = request.GET.get('city', '').strip()
    cities = DEFAULT_CITIES.copy()

    if city_input:
        cities.insert(0, city_input)

    weather_list = []
    errors = []

    seen = set()

    for city in cities:
        if city.casefold() in seen:
            continue
        seen.add(city.casefold())

        try:
            weather_list.append(get_weather(city))
        except requests.HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 404:
                errors.append(f'Город «{city}» не найден.')
            elif exc.response is not None and exc.response.status_code == 401:
                errors.append('Проверь API-ключ OpenWeatherMap.')
                break
            else:
                errors.append(f'Не удалось получить погоду для города {city}.')
        except requests.RequestException:
            errors.append(f'Ошибка соединения при запросе погоды для города {city}.')

    return render(request, 'weather/index.html', {
        'weather_list': weather_list,
        'errors': errors,
        'city': city_input,
    })
