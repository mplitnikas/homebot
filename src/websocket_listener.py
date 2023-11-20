import asyncio
import json
import threading
import websockets

class WebsocketListener:

    def __init__(self, homebot, websocket_url):
        self.homebot = homebot
        self.websocket_url = websocket_url

    async def websocket_client(self):
        print(f'Connecting to websocket at {self.websocket_url}')
        async with websockets.connect(self.websocket_url) as websocket:
            async for message in websocket:
                self.handle_event(message)

    def run(self):
        print('Starting websocket listener')
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.websocket_client())

    def handle_event(self, data):
        event = json.loads(data)
        match event:
            case {"attr": announcement}:
                # print(f"Received announcement: {announcement['id']}, {announcement['name']}")
                pass
            case {"e": "changed", "r": "lights", "id": id, "state": state}:
                print(f"Received state change for light id {id}: {state}")
                self.update_device(id, state)
            case {"e": "changed", "r": "groups", "id": id, "state": state}:
                print(f"Received group message: {event}")
                self.update_group(id, state)
            case {"r": "sensors"}:
                print(f"Received sensor data: {event}")
            case _:
                print(f"Received unknown event: {event}")

    def update_group(self, group_id, state):
        if self.homebot.groups.get(group_id):
            self.homebot.groups[group_id].all_on = state.get("all_on") or False
            self.homebot.groups[group_id].any_on = state.get("any_on") or False

    def update_device(self, device_id, state):
        self.homebot.devices[device_id].state.update(state)
