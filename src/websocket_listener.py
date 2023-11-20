import asyncio
import json
import redis
import threading
import websockets

class WebsocketListener:

    def __init__(self, websocket_url, redis_host, redis_port, redis_update_channel):
        self.websocket_url = websocket_url
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=0, decode_responses=True)
        self.redis_update_channel = redis_update_channel

    async def websocket_client(self):
        async with websockets.connect(self.websocket_url) as websocket:
            async for message in websocket:
                self.handle_event(message)

    def run(self):
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
                self.update_device(id, state)
            case {"e": "changed", "r": "groups", "id": id, "state": state}:
                self.update_group(id, state)
            case {"r": "sensors"}:
                # print(f"Received sensor data: {event}")
                pass
            case _:
                print(f"Received unknown event: {event}")

    def update_group(self, group_id, state):
        self.redis_client.publish(self.redis_update_channel, json.dumps({"type": "group", "group_id": group_id, "state": state}))

    def update_device(self, device_id, state):
        self.redis_client.publish(self.redis_update_channel, json.dumps({"type": "device", "device_id": device_id, "state": state}))
