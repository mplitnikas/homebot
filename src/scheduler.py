import schedule
import time
from datetime import datetime

class Scheduler:

    def __init__(self, homebot):
        self.homebot = homebot
        self.dispatcher = homebot.dispatcher
        self.weather_client = homebot.weather_client
        self.cc = homebot.color_calculator

    # time of day presets
    def noop(self):
        pass

    def predawn(self):
        self.preset_set(0, force_on=True)

    def night(self):
        self.preset_set(0)

    def twilight(self):
        self.preset_set(1)

    def sunrise_sunset(self):
        self.preset_set(2)

    def morning_evening(self):
        self.preset_set(3)

    def golden_hour(self):
        self.preset_set(4)

    def midday(self):
        self.preset_set(9)

    def preset_set(self, uv, force_on=False):
        weather = self.weather_client.get_last_weather()
        color_settings = self.cc.calculate_color_settings(weather, uv, force_on)
        self.dispatcher.set_group_state(self.homebot.MOOD_LIGHTS_GROUP, color_settings)

        non_color_settings = self.cc.calculate_non_color_settings(weather, uv, force_on)
        self.dispatcher.set_group_state(self.homebot.MAIN_LIGHTS_GROUP, non_color_settings)

    # =======

    def schedule_jobs(self):
        # update sunrise/sunset times overnight
        schedule.every().day.at("01:00").do(self.weather_client.update_sun_times)
        schedule.every(30).minutes.do(self.weather_client.update_weather)
        schedule.every(1).minutes.do(self.check_time_of_day)

    def run_jobs(self):
        while True:
            schedule.run_pending()
            time.sleep(60)

    # def set_group_state_from_weather(self):
    #     weather = self.weather_client.get_last_weather()
    #     uv = self.weather_client.get_last_uv()

    #     color_settings = self.cc.calculate_color_settings(weather, uv)
    #     self.dispatcher.set_group_state(MOOD_LIGHTS_GROUP, color_settings)

    #     non_color_settings = self.cc.calculate_non_color_settings(weather, uv)
    #     self.dispatcher.set_group_state(MAIN_LIGHTS_GROUP, non_color_settings)

    def check_time_of_day(self, now=None):
        now = now or datetime.now().astimezone()

        # ordered chronologically
        times_of_day = {
            'nightEnd': self.noop,
            'nauticalDawn': self.noop,
            'dawn': self.night,
            'sunrise': self.twilight,
            'sunriseEnd': self.golden_hour,
            'goldenHourEnd': self.midday,
            'solarNoon': self.midday,
            'goldenHour': self.golden_hour,
            'sunsetStart': self.sunrise_sunset,
            'sunset': self.twilight,
            'dusk': self.twilight,
            'nauticalDusk': self.night,
            'night': self.noop,
            'nadir': self.noop
        }
        sun_times = self.weather_client.get_sun_times()
        for time_of_day, time in sun_times.items():
            sun_time = datetime.fromisoformat(time).astimezone()
            if (now.hour, now.minute) == (sun_time.hour, sun_time.minute):
                times_of_day[time_of_day]()
