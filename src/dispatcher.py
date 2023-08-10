import json
import requests
import time
from functools import wraps

def retry(max_tries, initial_wait=10, max_wait=90):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            tries = 0
            while tries < max_tries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    tries += 1
                    wait_time = min(max_wait, initial_wait * 2 ** tries)
                    print(f'Error in {func.__name__}: {e}')
                    print(f'retrying ({tries}/{max_tries}) - waiting {wait_time} seconds')
                    if tries == max_tries:
                        raise
                    else:
                        time.sleep(wait_time)
        return wrapper
    return decorator

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

    @retry(max_tries=4)
    def get_devices(self):
        url = f'{self.api_url}/{self.api_key}/lights'
        response = requests.get(url)
        return [Device(device_info, device_id) for device_id, device_info in response.json().items()]

    @retry(max_tries=4)
    def get_groups(self):
        url = f'{self.api_url}/{self.api_key}/groups'
        response = requests.get(url)
        return response.json()

    @retry(max_tries=4)
    def get_group_all(self):
        url = f'{self.api_url}/{self.api_key}/groups/0'
        response = requests.get(url)
        return response.json()

    def is_all_off(self):
        return self.get_group_all()['state']['any_on'] == False
