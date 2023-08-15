from datetime import datetime

class ColorCalculator:

    def __init__(self, homebot):
        self.homebot = homebot

    def calculate_color_settings(self, uv: int, force_on=False):
        current_time = datetime.now().time()
        all_off = self.homebot.is_all_off()

        if all_off and not force_on:
            return {'on': False}

        rain_hue = 45000

        settings = self.uv_to_bulb_settings(uv)
        settings = {**settings, 'on': True}
        return settings

    def calculate_non_color_settings(self, uv: int, force_on=False):
        current_time = datetime.now().time()
        all_off = self.homebot.is_all_off()

        if (all_off and not force_on) or uv == 0:
            return {'on': False}

        settings = self.uv_to_bulb_settings(uv)
        settings = {'bri': settings['bri'], 'on': True}
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
