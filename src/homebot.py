#! /usr/bin/env python3

import json
import os
import redis
import sys
import threading
from dotenv import load_dotenv

from api import Api
from color_calculator import ColorCalculator
from device import Device
from dispatcher import Dispatcher
from scheduler import Scheduler
from weather_client import WeatherClient
from websocket_listener import WebsocketListener

from device import Device
from group import Group

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

    REDIS_HOST = os.getenv('REDIS_HOST')
    REDIS_PORT = os.getenv('REDIS_PORT')
    REDIS_UPDATE_CHANNEL = os.getenv('REDIS_UPDATE_CHANNEL') # device state updates etc

    def __init__(self):
        self.weather_client = WeatherClient(
            weather_api_url=self.WEATHER_API_URL,
            weather_api_key=self.WEATHER_API_KEY,
            weather_location=self.WEATHER_LOCATION,
            uv_api_url=self.UV_API_URL,
            uv_api_key=self.UV_API_KEY,
            uv_local_lat=self.LOCAL_LAT,
            uv_local_lng=self.LOCAL_LNG)
        self.color_calculator = ColorCalculator(self)
        self.dispatcher = Dispatcher(api_url=self.PHOSCON_API_URL, api_key=self.PHOSCON_API_KEY)
        self.scheduler = Scheduler(self)
        self.websocket_listener = WebsocketListener(
                websocket_url=self.PHOSCON_WEBSOCKETS_URL,
                redis_host=self.REDIS_HOST,
                redis_port=self.REDIS_PORT,
                redis_update_channel=self.REDIS_UPDATE_CHANNEL)

        self.devices = self.dispatcher.get_devices()
        self.groups = self.dispatcher.get_groups()
        group_all = Group(self.dispatcher.get_group_all(), self.ALL_LIGHTS_GROUP)
        self.groups[self.ALL_LIGHTS_GROUP] = group_all
        for group in self.groups.values():
            for light_id in group.lights:
                group.devices.append(self.devices[light_id])

        self.redis_client = redis.Redis(host=self.REDIS_HOST, port=self.REDIS_PORT, db=0, decode_responses=True)
        self.updates_subscriber = self.redis_client.pubsub(ignore_subscribe_messages=True)
        self.updates_subscriber.subscribe(**{self.REDIS_UPDATE_CHANNEL: self.updates_handler})

    def is_all_off(self):
        return self.dispatcher.is_all_off()

    def set_device_state(self, device_id, state):
        self.dispatcher.set_device_state(device_id, state)
        self.devices[device_id].custom_state = True

    def reset_device_state(self, device_id):
        # TODO reset device state to time of day preset
        self.devices[device_id].custom_state = False

    def set_group_state(self, group_id, state):
        self.dispatcher.set_group_state(group_id, state)
        for device in self.groups[group_id].devices:
            self.devices[device.id].custom_state = True

    def reset_group_state(self, group_id):
        # TODO reset group state to time of day preset
        for device in self.groups[group_id].devices:
            self.devices[device.id].custom_state = False

    # redis pubsub listeners

    def updates_handler(self, message):
        if message and message['data']:
            data = json.loads(message['data'])
            match data['type']:
                case "device":
                    self.update_device(data['device_id'], data['state'])
                case "group":
                    self.update_group(data['group_id'], data['state'])
                case _:
                    print(f"Received unknown message type: {data}")

    def update_group(self, group_id, state):
        if self.groups.get(group_id):
            self.groups[group_id].state.update(state)
        else:
            print(f"Received update for unknown group id {group_id}")

    def update_device(self, device_id, state):
        if self.devices.get(device_id):
            self.devices[device_id].state.update(state)
        else:
            print(f"Received update for unknown device id {device_id}")

if __name__ == '__main__' and not sys.flags.interactive:
    homebot = Homebot()
    homebot.scheduler.schedule_jobs()
    job_runner = threading.Thread(target=homebot.scheduler.run_jobs)
    job_runner.start()
    # api_runner = threading.Thread(target=Api.run, daemon=True)
    # api_runner.start()
    websocket_runner = threading.Thread(target=homebot.websocket_listener.run)
    websocket_runner.start()

    homebot.updates_subscriber.run_in_thread(sleep_time=0.001)
