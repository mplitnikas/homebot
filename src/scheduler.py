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

    def night(self):
        self.preset_set(0)

    def predawn(self):
        self.preset_set(0, force_on=True)

    def twilight(self):
        self.preset_set(1)

    def sunrise_sunset(self):
        self.preset_set(3)

    def morning_evening(self):
        self.preset_set(4)

    def golden_hour(self):
        self.preset_set(6)

    def midday(self):
        self.preset_set(9)

    def preset_set(self, uv, force_on=False):
        color_settings = self.cc.calculate_color_settings(uv, force_on)
        self.dispatcher.set_group_state(self.homebot.MOOD_LIGHTS_GROUP, color_settings)

        non_color_settings = self.cc.calculate_non_color_settings(uv, force_on)
        self.dispatcher.set_group_state(self.homebot.MAIN_LIGHTS_GROUP, non_color_settings)

    # =======

    def schedule_jobs(self):
        # update sunrise/sunset times overnight
        schedule.every().day.at("01:00").do(self.weather_client.update_sun_times)
        schedule.every(1).minutes.do(self.check_time_of_day)

    def run_jobs(self):
        while True:
            schedule.run_pending()
            time.sleep(60)

    def check_time_of_day(self, time_of_day=None):
        if time_of_day is None:
            now = datetime.now()
            time_of_day = str((now.hour, now.minute))

        # ordered chronologically
        times_of_day = {
            'nightEnd': self.noop,
            'nauticalDawn': self.noop,
            'dawn': self.predawn,
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
            'nadir': self.noop,
            None: self.noop
        }
        sun_times = self.weather_client.get_sun_times()
        matching_time = sun_times.get(time_of_day)
        times_of_day[matching_time]()
