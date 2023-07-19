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
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv('BASE_URL')
API_PORT = os.getenv('API_PORT')
WEBSOCKETS_PORT = os.getenv('WEBSOCKETS_PORT')
WEBSOCKETS_URL = f'ws://{BASE_URL}:8081'
API_URL = f'http://{BASE_URL}:8080/api'
API_KEY = os.getenv('API_KEY')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
WEATHER_API_URL = os.getenv('WEATHER_API_URL')

ALL_LIGHTS_GROUP = os.getenv('ALL_LIGHTS_GROUP')
LIVING_ROOM_GROUP = os.getenv('LIVING_ROOM_GROUP')
MOOD_LIGHTS_GROUP = os.getenv('MOOD_LIGHTS_GROUP')
MAIN_LIGHTS_GROUP = os.getenv('MAIN_LIGHTS_GROUP')
BEDROOM_LIGHTS_GROUP = os.getenv('BEDROOM_LIGHTS_GROUP')

class Homebot:
    def __init__(self):
        self.dispatcher = Dispatcher()
        self.scheduler = Scheduler(self.dispatcher)
        # self.websocket_listener = WebsocketListener()
        self.selected_device = None
        self.selected_group = None
        self.devices = []
        self.groups = []

        # self.get_devices()

    def get_devices(self):
        self.devices = self.dispatcher.get_devices()
        return self.devices

    # update light state from websocket event

    # handle button events from remote incl long-press & double-click
    # leave non-simple press events for later, may not be needed
    # for now, just toggle all lights off / on in current state for schedule

class Scheduler:
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        # self.schedule_jobs()
        # self.run_jobs() # TODO run in separate thread

    def schedule_jobs(self):
        schedule.every().day.at('08:30').do(self.morning)
        schedule.every().day.at('11:00').do(self.afternoon)
        schedule.every().day.at('18:00').do(self.evening)
        schedule.every().day.at('20:30').do(self.night)

    def run_jobs(self):
        while True:
            schedule.run_pending()
            time.sleep(10)

    def morning(self):
        self.dispatcher.set_group_state(MOOD_LIGHTS_GROUP, {'on': True, 'bri': 255, 'ct': 500})
        self.dispatcher.set_group_state(MAIN_LIGHTS_GROUP, {'on': True, 'bri': 255})

    def afternoon(self):
        self.dispatcher.set_group_state(MOOD_LIGHTS_GROUP, {'on': True, 'bri': 255, 'ct': 300})
        self.dispatcher.set_group_state(MAIN_LIGHTS_GROUP, {'on': True, 'bri': 255})

    def evening(self):
        self.dispatcher.set_group_state(MOOD_LIGHTS_GROUP, {'on': True, 'bri': 150, 'hue': 4000, 'sat': 255})
        self.dispatcher.set_group_state(MAIN_LIGHTS_GROUP, {'on': True, 'bri': 80})

    def night(self):
        self.dispatcher.set_group_state(MOOD_LIGHTS_GROUP, {'on': True, "hue": 1600, "sat": 255, "bri": 120})
        self.dispatcher.set_group_state(MAIN_LIGHTS_GROUP, {'on': False})

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

    # get groups via API

    # ! scenes may not work with the sengled bulbs - may need to make manually
    # get scenes
    # recall scenes

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
