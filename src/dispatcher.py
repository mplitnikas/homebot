import json
import requests
from decorators import retry
from device import Device
from group import Group

class Dispatcher:

    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.api_key = api_key

    @retry(max_tries=4)
    def set_device_state(self, device_id: str, state: dict):
        url = f'{self.api_url}/{self.api_key}/lights/{device_id}/state'
        response = requests.put(url, json.dumps(state))
        return response

    @retry(max_tries=4)
    def set_group_state(self, group_id: str, state: dict):
        url = f'{self.api_url}/{self.api_key}/groups/{group_id}/action'
        response = requests.put(url, json.dumps(state))
        return response

    def get_group(self, group_id: str):
        url = f'{self.api_url}/{self.api_key}/groups/{group_id}'
        response = requests.get(url)
        return response.json()

    def get_device(self, device_id: str):
        url = f'{self.api_url}/{self.api_key}/lights/{device_id}'
        response = requests.get(url)
        return response.json()

    @retry(max_tries=4)
    def get_devices(self):
        url = f'{self.api_url}/{self.api_key}/lights'
        response = requests.get(url)
        device_list = [Device(device_info, device_id) for device_id, device_info in response.json().items()]
        return {device.id: device for device in device_list}

    @retry(max_tries=4)
    def get_groups(self):
        url = f'{self.api_url}/{self.api_key}/groups'
        response = requests.get(url)
        group_list = [Group(group_info, group_id) for group_id, group_info in response.json().items()]
        return {group.id: group for group in group_list}

    @retry(max_tries=4)
    def get_group_all(self):
        url = f'{self.api_url}/{self.api_key}/groups/0'
        response = requests.get(url)
        return response.json()

    def is_all_off(self):
        return self.get_group_all()['state']['any_on'] == False
