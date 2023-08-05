import json
import requests

class Dispatcher:

    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.api_key = api_key

    def set_device_state(self, device_id: str, state: dict):
        url = f'{self.api_url}/{self.api_key}/lights/{device_id}/state'
        response = requests.put(url, json.dumps(state))
        return response
        # TODO decode & handle response

    def set_group_state(self, group_id: str, state: dict):
        url = f'{self.api_url}/{self.api_key}/groups/{group_id}/action'
        response = requests.put(url, json.dumps(state))
        return response
        # TODO decode & handle response

    def get_devices(self):
        url = f'{self.api_url}/{self.api_key}/lights'
        response = requests.get(url)
        return [Device(device_info, device_id) for device_id, device_info in response.json().items()]

    def get_groups(self):
        url = f'{self.api_url}/{self.api_key}/groups'
        response = requests.get(url)
        return response.json()

    def get_group_all(self):
        url = f'{self.api_url}/{self.api_key}/groups/0'
        response = requests.get(url)
        return response.json()

    def is_all_off(self):
        return self.get_group_all()['state']['any_on'] == False
