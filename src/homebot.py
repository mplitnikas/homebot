#! /usr/bin/env python3

import os
import sys
from dotenv import load_dotenv

from color_calculator import ColorCalculator
from device import Device
from dispatcher import Dispatcher
from scheduler import Scheduler
from weather_client import WeatherClient
from api import Api
# from websocket_listener import WebsocketListener

load_dotenv()

class Homebot:

    PHOSCON_BASE_URL = os.getenv('PHOSCON_BASE_URL')
    PHOSCON_API_PORT = os.getenv('PHOSCON_API_PORT')
    PHOSCON_WEBSOCKETS_PORT = os.getenv('PHOSCON_WEBSOCKETS_PORT')
    PHOSCON_WEBSOCKETS_URL = f'ws://{PHOSCON_BASE_URL}:{PHOSCON_WEBSOCKETS_PORT}'
    PHOSCON_API_URL = f'http://{PHOSCON_BASE_URL}:{PHOSCON_API_PORT}/api'
    PHOSCON_API_KEY = os.getenv('PHOSCON_API_KEY')
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

    def __init__(self):
        self.weather_client = WeatherClient(
            weather_api_url=self.WEATHER_API_URL,
            weather_api_key=self.WEATHER_API_KEY,
            weather_location=self.WEATHER_LOCATION,
            uv_api_url=self.UV_API_URL,
            uv_api_key=self.UV_API_KEY,
            uv_local_lat=self.LOCAL_LAT,
            uv_local_lng=self.LOCAL_LNG
        )
        self.color_calculator = ColorCalculator(self)
        self.dispatcher = Dispatcher(api_url=self.PHOSCON_API_URL, api_key=self.PHOSCON_API_KEY)
        self.scheduler = Scheduler(self)
        # self.websocket_listener = WebsocketListener()
        # self.selected_device = None
        # self.selected_group = None
        # self.devices = self.get_devices()
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


if __name__ == '__main__' and not sys.flags.interactive:
    homebot = Homebot()
    homebot.scheduler.schedule_jobs()
    homebot.scheduler.run_jobs()
    home.api.run()
    # TODO thread these
