import json
import os
import requests
from datetime import datetime

class WeatherClient:

    def __init__(self, weather_api_url, weather_api_key, weather_location, uv_api_url, uv_api_key, uv_local_lat, uv_local_lng):
        self.weather_api_url = weather_api_url
        self.weather_api_key = weather_api_key
        self.weather_location = weather_location
        self.uv_api_url = uv_api_url
        self.uv_api_key = uv_api_key
        self.uv_local_lat = uv_local_lat
        self.uv_local_lng = uv_local_lng
        self.last_weather = None

    def get_last_weather(self):
        return self.last_weather

    def get_last_uv(self):
        path = 'last_uv.json'
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.loads(f)

    def update_weather(self):
        url = f'{self.weather_api_url}/current.json'
        try:
            response = requests.get(url, params={'key': self.weather_api_key, 'q': self.weather_location})
            resp = response.json()
            self.last_weather = resp
        except Exception as e:
            print('=' * 5, datetime.now(), '=' * 5)
            print('error fetching weather: ', e)

    def update_uv(self):
        try:
            response = requests.get(self.uv_api_url, params={'lat': self.uv_local_lat, 'lng': self.uv_local_lng}, headers={'x-access-token': self.uv_api_key})
            resp = response.json()
            with open('last_uv.json', 'w') as f:
                json.dump(resp, f)
        except Exception as e:
            print('=' * 5, datetime.now(), '=' * 5)
            print('error fetching uv: ', e)
