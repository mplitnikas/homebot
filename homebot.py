#! /usr/bin/env python3

import asyncio
import json
import os
import requests
import schedule
import sys
import threading
import time
import websockets
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv('BASE_URL')
API_PORT = os.getenv('API_PORT')
WEBSOCKETS_PORT = os.getenv('WEBSOCKETS_PORT')
WEBSOCKETS_URL = f'ws://{BASE_URL}:{WEBSOCKETS_PORT}'
API_URL = f'http://{BASE_URL}:{API_PORT}/api'
API_KEY = os.getenv('API_KEY')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
WEATHER_API_URL = os.getenv('WEATHER_API_URL')
WEATHER_LOCATION = os.getenv('WEATHER_LOCATION')
UV_API_URL = os.getenv('UV_API_URL')
UV_API_KEY = os.getenv('UV_API_KEY')
LOCAL_LAT = os.getenv('LOCAL_LAT')
LOCAL_LNG = os.getenv('LOCAL_LNG')

ALL_LIGHTS_GROUP = os.getenv('ALL_LIGHTS_GROUP')
LIVING_ROOM_GROUP = os.getenv('LIVING_ROOM_GROUP')
MOOD_LIGHTS_GROUP = os.getenv('MOOD_LIGHTS_GROUP')
MAIN_LIGHTS_GROUP = os.getenv('MAIN_LIGHTS_GROUP')
BEDROOM_LIGHTS_GROUP = os.getenv('BEDROOM_LIGHTS_GROUP')

class Homebot:
    def __init__(self):
        self.weather_client = WeatherClient()
        self.color_calculator = ColorCalculator(self)
        self.dispatcher = Dispatcher()
        self.scheduler = Scheduler(self)
        # self.websocket_listener = WebsocketListener()
        # self.selected_device = None
        # self.selected_group = None
        self.devices = self.get_devices()
        # self.groups = []

    def get_devices(self):
        return self.dispatcher.get_devices()

    def update_devices(self):
        self.devices = self.get_devices()

    def is_all_off(self):
        return self.dispatcher.is_all_off()

    # update light state from websocket event

    # handle button events from remote incl long-press & double-click
    # leave non-simple press events for later, may not be needed
    # for now, just toggle all lights off / on in current state for schedule

class WeatherClient:

    def __init__(self):
        self.last_weather_json = None
        self.last_uv_json = None

    def get_current_weather(self):
        url = f'{WEATHER_API_URL}/current.json'
        try:
            response = requests.get(url, params={'key': WEATHER_API_KEY, 'q': WEATHER_LOCATION})
            json = response.json()
            self.last_weather_json = json
            return json
        except Exception as e:
            print('=' * 5, datetime.now(), '=' * 5)
            print('error fetching weather: ', e)
            return self.read_last_weather_json()

    def get_current_uv(self):
        try:
            response = requests.get(UV_API_URL, params={'lat': LOCAL_LAT, 'lng': LOCAL_LNG}, headers={'x-access-token': UV_API_KEY})
            json = response.json()
            self.last_uv_json = json
            return json
        except Exception as e:
            print('=' * 5, datetime.now(), '=' * 5)
            print('error fetching uv: ', e)
            return self.read_last_uv_json()

class ColorCalculator:

    def __init__(self, homebot):
        self.homebot = homebot

    def calculate_color_settings(self, weather_json, uv_json):
        current_time = datetime.now().time()
        all_off = self.homebot.is_all_off()

        if all_off and (current_time.hour < 8 or current_time.hour >= 21):
            return {'on': False}

        rain_hue = 45000

        settings = self.uv_to_bulb_settings(uv_json['result']['uv'])
        settings = {**settings, 'on': True}
        if weather_json['current']['is_day'] == 1 and self.is_inclement_weather(weather_json):
            settings['hue'] = rain_hue
            settings['sat'] = max(settings['sat'] * 2, 255)
            settings['bri'] = int(settings['bri'] * 0.7)
        return settings

    def calculate_non_color_settings(self, weather_json, uv_json):
        current_time = datetime.now().time()
        all_off = self.homebot.is_all_off()

        if all_off and (current_time.hour < 8 or current_time.hour >= 21):
            return {'on': False}

        settings = self.uv_to_bulb_settings(uv_json['result']['uv'])
        settings = {'bri': settings['bri'], 'on': True}
        if weather_json['current']['is_day'] == 1 and self.is_inclement_weather(weather_json):
            settings['bri'] = int(settings['bri'] * 0.7)
        if weather_json['current']['is_day'] == 0:
            settings['bri'] = 0
            settings['on'] = False
        return settings

    def uv_to_bulb_settings(self, uv_index):
        # Maximum UV index you defined
        uv_max = 9
        if uv_index > uv_max:
            uv_index = uv_max

        # Bulb settings at maximum UV index (midday: bright and white)
        bri_max = 255
        hue_max = 8000
        sat_max = 255

        # Bulb settings at minimum UV index (sunrise/sunset: dim and red)
        bri_min = 120
        hue_min = 1600
        sat_min = 25

        # Calculate the bulb settings based on the current UV index
        bri = int((uv_index / uv_max) * (bri_max - bri_min) + bri_min)
        hue = int((uv_index / uv_max) * (hue_max - hue_min) + hue_min)
        sat = int((1 - uv_index / uv_max) * (sat_max - sat_min) + sat_min)  # Inverse relationship

        # Return the bulb settings as a dictionary
        return {"bri": bri, "hue": hue, "sat": sat}

    def is_inclement_weather(self, weather_json):
        clement_weather_codes = [1000, 1003, 1006, 1009, 1030]
        return weather_json['current']['condition']['code'] not in clement_weather_codes

class Scheduler:
    def __init__(self, homebot):
        self.homebot = homebot
        self.dispatcher = homebot.dispatcher
        self.weather_client = homebot.weather_client
        self.color_calculator = homebot.color_calculator

    def schedule_jobs(self):
        schedule.every(5).minutes.do(self.update_weather_json)
        schedule.every(36).minutes.do(self.update_uv_json)
        schedule.every(1).minutes.do(self.set_group_state_from_weather)

    def run_jobs(self):
        while True:
            schedule.run_pending()
            time.sleep(60)

    def update_weather_json(self):
        self.weather_client.get_current_weather()

    def update_uv_json(self):
        self.weather_client.get_current_uv()

    def set_group_state_from_weather(self):
        weather = self.weather_client.last_weather_json or self.weather_client.get_current_weather()
        uv = self.weather_client.last_uv_json or self.weather_client.get_current_uv()

        color_settings = self.color_calculator.calculate_color_settings(weather, uv)
        self.dispatcher.set_group_state(MOOD_LIGHTS_GROUP, color_settings)

        non_color_settings = self.color_calculator.calculate_non_color_settings(weather, uv)
        self.dispatcher.set_group_state(MAIN_LIGHTS_GROUP, non_color_settings)


class Device:
    def __init__(self, device_info, device_id):
        device_state = device_info["state"]
        state = {
            'on': device_state.get("on"),
            'bri': device_state.get("bri"),
            'hue': device_state.get("hue"),
            'sat': device_state.get("sat"),
            'effect': device_state.get("effect"),
            'xy': device_state.get("xy"),
            'ct': device_state.get("ct"),
            'alert': device_state.get("alert"),
            'colormode': device_state.get("colormode"),
            'mode': device_state.get("mode"),
            'reachable': device_state.get("reachable")
        }
        self.name = device_info.get("name")
        self.type = device_info.get("type")
        self.id = device_id
        self.state = state
        self.has_color = device_info.get("hascolor")
        self.color_capabilities = device_info.get("color_capabilities")
        self.capabilities = device_info.get("capabilities")

    #name: nil, type: nil, id: nil, state: %{}, has_color: false, color_capabilities: 0, capabilities: %{}

class Dispatcher:

    def set_device_state(self, device_id: str, state: dict):
        url = f'{API_URL}/{API_KEY}/lights/{device_id}/state'
        response = requests.put(url, json.dumps(state))
        return response
        # TODO decode & handle response

    def set_group_state(self, group_id: str, state: dict):
        url = f'{API_URL}/{API_KEY}/groups/{group_id}/action'
        response = requests.put(url, json.dumps(state))
        return response
        # TODO decode & handle response

    def get_devices(self):
        url = f'{API_URL}/{API_KEY}/lights'
        response = requests.get(url)
        return [Device(device_info, device_id) for device_id, device_info in response.json().items()]

    def get_groups(self):
        url = f'{API_URL}/{API_KEY}/groups'
        response = requests.get(url)
        return response.json()

    def get_group_all(self):
        url = f'{API_URL}/{API_KEY}/groups/0'
        response = requests.get(url)
        return response.json()

    def is_all_off(self):
        return self.get_group_all()['state']['any_on'] == False

class WebsocketListener:

    def __init__(self):
        threading.Thread(target=self.run_listener, daemon=True).start()

    def handle_event(self, event):
        print(event)

    async def websocket_client(self):
        async with websockets.connect(WEBSOCKETS_URL) as websocket:
            async for message in websocket:
                self.handle_event(message)

    def run_listener(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.websocket_client())
        loop.run_forever()


    # note this is blocking & only gets one message before exiting
    # use await to make non-blocking? https://pypi.org/project/websockets/

    # handle incoming frames & pattern match diff message types
    # see https://benhoyt.com/writings/python-pattern-matching/

if __name__ == '__main__' and not sys.flags.interactive:
    homebot = Homebot()
    homebot.scheduler.schedule_jobs()
    homebot.scheduler.run_jobs()
