class Device:

    #name: nil, type: nil, id: nil, state: %{}, has_color: false, color_capabilities: 0, capabilities: %{}

    def __init__(self, device_info, device_id):
        device_state = device_info["state"]
        state = {
            'on': device_state.get("on"),
            'bri': device_state.get("bri"),
            'hue': device_state.get("hue"),
            'sat': device_state.get("sat"),
            'effect': device_state.get("effect"),
            'xy': device_state.get("xy"),
            'ct': device_state.get("ct"),
            'alert': device_state.get("alert"),
            'colormode': device_state.get("colormode"),
            'mode': device_state.get("mode"),
            'reachable': device_state.get("reachable")
        }
        self.name = device_info.get("name")
        self.type = device_info.get("type")
        self.id = device_id
        self.state = state
        self.has_color = device_info.get("hascolor")
        self.color_capabilities = device_info.get("color_capabilities")
        self.capabilities = device_info.get("capabilities")

        # set to true if device state is set directly by user
        self.custom_state = False

    def __repr__(self):
        return f'''
        name: {self.name}
        type: {self.type}
        id: {self.id}
        state: {self.state}
        custom_state: {self.custom_state}
        '''
