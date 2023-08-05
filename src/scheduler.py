import schedule
import time

class Scheduler:
    def __init__(self, homebot):
        self.homebot = homebot
        self.dispatcher = homebot.dispatcher
        self.weather_client = homebot.weather_client
        self.color_calculator = homebot.color_calculator

    def schedule_jobs(self):
        schedule.every(30).minutes.do(self.weather_client.update_weather)
        schedule.every().day.at("12:00").do(self.weather_client.update_uv)
        schedule.every(1).minutes.do(self.set_group_state_from_weather)

    def run_jobs(self):
        while True:
            schedule.run_pending()
            time.sleep(60)

    def set_group_state_from_weather(self):
        weather = self.weather_client.get_last_weather()
        uv = self.weather_client.get_last_uv()

        color_settings = self.color_calculator.calculate_color_settings(weather, uv)
        self.dispatcher.set_group_state(MOOD_LIGHTS_GROUP, color_settings)

        non_color_settings = self.color_calculator.calculate_non_color_settings(weather, uv)
        self.dispatcher.set_group_state(MAIN_LIGHTS_GROUP, non_color_settings)
