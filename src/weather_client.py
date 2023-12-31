import json
import os
import requests
import traceback
from datetime import datetime
from dateutil.parser import parse
from decorators import retry

class WeatherClient:

    def __init__(self, weather_api_url, weather_api_key, weather_location,
                 uv_api_url, uv_api_key, uv_local_lat, uv_local_lng):
        self.weather_api_url = weather_api_url
        self.weather_api_key = weather_api_key
        self.weather_location = weather_location
        self.uv_api_url = uv_api_url
        self.uv_api_key = uv_api_key
        self.uv_local_lat = uv_local_lat
        self.uv_local_lng = uv_local_lng
        self.last_weather = None

    def get_last_weather(self):
        if not self.last_weather:
            self.update_weather()
        return self.last_weather

    def get_last_uv(self):
        path = 'last_uv.json'
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.loads(f.read())

    def get_sun_times(self):
        path = 'sun_times.json'
        if not os.path.exists(path):
            self.update_sun_times()
        with open(path, 'r') as f:
            return json.loads(f.read())

    def convert_sun_times(self, data):
        sun_info = data['result']['sun_info']['sun_times']
        # list comprehension to convert sun_time: utc_time to "HH:MM": sun_time
        return {f"{parse(v).astimezone().hour:02}:{parse(v).astimezone().minute:02}": k
                for k, v in sun_info.items()}

    @retry(max_tries=3, fail_silent=True)
    def update_weather(self):
        url = f'{self.weather_api_url}/current.json'
        response = requests.get(url, params={'key': self.weather_api_key, 'q': self.weather_location})
        resp = response.json()
        self.last_weather = resp

    @retry(max_tries=3, fail_silent=True)
    def update_sun_times(self):
        response = requests.get(
            self.uv_api_url,
            params={'lat': self.uv_local_lat, 'lng': self.uv_local_lng},
            headers={'x-access-token': self.uv_api_key}
        )
        resp = response.json()
        st = self.convert_sun_times(resp)
        with open('sun_times.json', 'w') as f:
            json.dump(st, f)
