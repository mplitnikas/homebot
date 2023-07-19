import json
import unittest
from unittest import mock

import homebot

class HomebotTests(unittest.TestCase):
    def setUp(self):
        self.homebot = homebot.Homebot()

    def test_init(self):
        self.assertEqual(self.homebot.devices, [])
        self.assertEqual(self.homebot.selected_device, None)
        self.assertEqual(self.homebot.selected_group, None)

    @mock.patch('homebot.Dispatcher.get_devices')
    def test_get_lights(self, mock_get_devices):
        mock_get_devices.return_value = [1, 2, 3]
        self.assertEqual(self.homebot.get_devices(), [1, 2, 3])
        self.assertEqual(self.homebot.devices, [1, 2, 3])

class DispatcherTests(unittest.TestCase):
    def setUp(self):
        self.dispatcher = homebot.Dispatcher()

    @mock.patch('requests.get')
    def test_get_devices(self, mock_get):
        mock_get.return_value.json.return_value = [1, 2, 3]
        self.assertEqual(self.dispatcher.get_devices(), [1, 2, 3])

if __name__ == '__main__':
    unittest.main()
