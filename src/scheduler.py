import redis

class Scheduler:

    def __init__(self, dispatcher, color_calculator, redis_host, redis_port, redis_time_channel):
        self.dispatcher = dispatcher
        self.cc = color_calculator
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_time_channel = redis_time_channel

        self.redis_client = redis.Redis(host=self.redis_host, port=self.redis_port, db=0, decode_responses=True)
        self.updates_subscriber = self.redis_client.pubsub(ignore_subscribe_messages=True)
        self.updates_subscriber.subscribe(**{self.redis_time_channel: self.time_event_handler})

    def run(self):
        self.updates_subscriber.run_in_thread(sleep_time=0.01)

    def time_event_handler(self, message):
        if message and message['data']:
            event = json.loads(message['data'])
            match event:
                case 'dawn':
                    self.preset_set(0, force_on=True)
                case 'sunrise':
                    self.preset_set(1)
                case 'sunriseEnd':
                    self.preset_set(6)
                case 'goldenHourEnd':
                    self.preset_set(9)
                case 'solarNoon':
                    self.preset_set(9)
                case 'goldenHour':
                    self.preset_set(6)
                case 'sunsetStart':
                    self.preset_set(3)
                case 'sunset':
                    self.preset_set(1)
                case 'dusk':
                    self.preset_set(1)
                case 'nauticalDusk':
                    self.preset_set(0)
                case 'night' | 'nadir' | 'nightEnd' | 'nauticalDawn':
                    pass
                case _:
                    print(f"Received unknown time event: {event}")

    def preset_set(self, uv, force_on=False):
        color_settings = self.cc.calculate_color_settings(uv, force_on)
        self.dispatcher.set_group_state(self.homebot.MOOD_LIGHTS_GROUP, color_settings)

        non_color_settings = self.cc.calculate_non_color_settings(uv, force_on)
        self.dispatcher.set_group_state(self.homebot.MAIN_LIGHTS_GROUP, non_color_settings)
