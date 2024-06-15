import requests
from django.shortcuts import render
from .forms import CityForm
from django.conf import settings
import datetime
from django.http import JsonResponse
def city_suggestions(request):
    if 'term' in request.GET:
        city_name = request.GET.get('term')
        country_code = request.GET.get('country', '')
        
        url = f"https://wft-geo-db.p.rapidapi.com/v1/geo/cities?namePrefix={city_name}&minPopulation=10000"
        if country_code:
            url += f"&countryIds={country_code}"
            
        headers = {
            "x-rapidapi-key": settings.GEO_DB_API_KEY,
            "x-rapidapi-host": settings.GEO_DB_API_HOST
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json().get('data', [])
            suggestions = [{'value': f"{city['latitude']} {city['longitude']}", 'label': f"{city['city']}, {city['countryCode']}"} for city in data]
            return JsonResponse(suggestions, safe=False)
    return JsonResponse([], safe=False)


def get_city_time(city_name, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        timezone_offset = data['timezone']
        local_time = datetime.datetime.utcfromtimestamp(data['dt']) + datetime.timedelta(seconds=timezone_offset)
        return local_time
    else:
        return None

def get_geo_data(city_name, country_code=None):
    url = f"https://wft-geo-db.p.rapidapi.com/v1/geo/cities?namePrefix={city_name}"
    if country_code:
        url += f"&countryIds={country_code}"
    headers = {
        "x-rapidapi-key": settings.GEO_DB_API_KEY,
        "x-rapidapi-host": settings.GEO_DB_API_HOST
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200 or 'data' not in response.json():
        return None
    data = response.json()['data']
    if len(data) == 0:
        return None
    return data[0]

def get_weather_data(lat, lon):
    api_key = settings.OPENWEATHER_API_KEY
    url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric'
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    if 'main' not in data or 'weather' not in data:
        return None
    return data

def get_forecast_data(lat, lon):
    api_key = settings.OPENWEATHER_API_KEY
    url = f'http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric'
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    if 'list' not in data:
        return None
    
    forecast_data = []
    for entry in data['list']:
        if '12:00:00' in entry['dt_txt']:
            forecast_data.append({
                'datetime': entry['dt_txt'],
                'temperature': entry['main']['temp'],
                'description': entry['weather'][0]['description'],
                'icon': entry['weather'][0]['icon'],
                'temp_min': entry['main']['temp_min'],
                'temp_max': entry['main']['temp_max'],
                'humidity': entry['main']['humidity'],
                'speed': entry['wind']['speed'],
                'pressure': entry['main']['pressure'],

            })
            if len(forecast_data) == 5: 
                break

    return forecast_data

def home(request):
    form = CityForm()
    weather_data = None
    forecast_data = None
    local_time = None
    background = 'night'  

    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            city_name = form.cleaned_data['name']
            country_code = form.cleaned_data.get('country', '')
            
            geo_data = get_geo_data(city_name, country_code)
            if geo_data:
                lat = geo_data['latitude']
                lon = geo_data['longitude']
                local_time = get_city_time(city_name, settings.OPENWEATHER_API_KEY)
                if local_time:
                    current_hour = local_time.hour
                    if 4 <= current_hour < 10:
                        background = 'morning'
                    elif 10 <= current_hour < 16:
                        background = 'afternoon'
                    elif 16 <= current_hour < 20:
                        background = 'evening'
                
                data = get_weather_data(lat, lon)
                if data:
                    weather_data = {
                        'city': city_name,
                        'icon': data['weather'][0]['icon'],
                        'temperature': data['main']['temp'],
                        'description': data['weather'][0]['description'],
                        'temp_min': data['main']['temp_min'],
                        'temp_max': data['main']['temp_max'],
                        'humidity': data['main']['humidity'],
                        'speed': data['wind']['speed'],
                        'pressure': data['main']['pressure'],
                    }
                forecast_data = get_forecast_data(lat, lon)

    context = {
        'form': form,
        'weather_data': weather_data,
        'forecast_data': forecast_data,
        'local_time': local_time,
        'background': background
    }

    return render(request, 'weatherapp/HTML/home.html', context)

