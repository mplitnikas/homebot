from datetime import datetime

class ColorCalculator:

    def __init__(self, homebot):
        self.homebot = homebot

    def calculate_color_settings(self, weather_json, uv_json):
        current_time = datetime.now().time()
        all_off = self.homebot.is_all_off()

        if all_off and (current_time.hour < 8 or current_time.hour >= 21):
            return {'on': False}

        rain_hue = 45000

        settings = self.uv_to_bulb_settings(uv_json['result']['uv'])
        settings = {**settings, 'on': True}
        if weather_json['current']['is_day'] == 1 and self.is_inclement_weather(weather_json):
            settings['hue'] = rain_hue
            settings['sat'] = max(settings['sat'] * 2, 255)
            settings['bri'] = int(settings['bri'] * 0.7)
        return settings

    def calculate_non_color_settings(self, weather_json, uv_json):
        current_time = datetime.now().time()
        all_off = self.homebot.is_all_off()

        if all_off and (current_time.hour < 8 or current_time.hour >= 21):
            return {'on': False}

        settings = self.uv_to_bulb_settings(uv_json['result']['uv'])
        settings = {'bri': settings['bri'], 'on': True}
        if weather_json['current']['is_day'] == 1 and self.is_inclement_weather(weather_json):
            settings['bri'] = int(settings['bri'] * 0.7)
        if weather_json['current']['is_day'] == 0:
            settings['bri'] = 0
            settings['on'] = False
        return settings

    def uv_to_bulb_settings(self, uv_index):
        # Maximum UV index you defined
        uv_max = 9
        if uv_index > uv_max:
            uv_index = uv_max

        # Bulb settings at maximum UV index (midday: bright and white)
        bri_max = 255
        hue_max = 8000
        sat_max = 255

        # Bulb settings at minimum UV index (sunrise/sunset: dim and red)
        bri_min = 120
        hue_min = 1600
        sat_min = 25

        # Calculate the bulb settings based on the current UV index
        bri = int((uv_index / uv_max) * (bri_max - bri_min) + bri_min)
        hue = int((uv_index / uv_max) * (hue_max - hue_min) + hue_min)
        sat = int((1 - uv_index / uv_max) * (sat_max - sat_min) + sat_min)  # Inverse relationship

        # Return the bulb settings as a dictionary
        return {"bri": bri, "hue": hue, "sat": sat}

    def is_inclement_weather(self, weather_json):
        clement_weather_codes = [1000, 1003, 1006, 1009, 1030]
        return weather_json['current']['condition']['code'] not in clement_weather_codes
