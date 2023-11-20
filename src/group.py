class Group:

    # {'action': 
    #  {'alert': 'none', 'bri': 255, 'colormode': 'hs', 'ct': 0, 'effect': 'none', 'hue': 7999, 'on': True, 'sat': 25, 'scene': None, 'xy': [0, 0]},
    #  'devicemembership': [],
    #  'etag': 'c425f6af863a5bd26fea220958c9f8c2',
    #  'id': '4',
    #  'lights': ['4', '6', '1', '3', '5'],
    #  'name': 'mood lights',
    #  'scenes': [{'id': '1', 'lightcount': 1, 'name': 'green', 'transitiontime': 10}],
    #  'state': {'all_on': True, 'any_on': True},
    #  'type': 'LightGroup'}

    def __init__(self, group_info, group_id):
        self.name = group_info.get("name")
        self.id = group_id
        self.state = group_info.get("state")
        self.lights = group_info.get("lights")
        self.devices = []

        # set to true if any light state in group is set directly by user
        self.custom_state = False

    def is_custom_state(self):
        return any([device.custom_state for device in self.devices])

    def __repr__(self):
        return f'''
        name: {self.name}
        id: {self.id}
        state: {self.state}
        lights: {self.lights}
        custom_state: {self.custom_state}
        '''
