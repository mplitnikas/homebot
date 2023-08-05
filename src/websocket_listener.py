import asyncio
import threading
import websockets

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
