#!/usr/bin/env python3

"""
Helper to find the desired PortAudio device.
"""

import os
import re
import sys
import wave

import pyaudio

from c3lingo_mumble.stdchannel_redirected import stdchannel_redirected

class Audio:
    def __init__(self):
        with stdchannel_redirected(sys.stderr, os.devnull):
            self.pyaudio = pyaudio.PyAudio()

    def get_devinfo(self, regex, min_input_channels=1, min_output_channels=1):
        if regex.isdigit():
            return self.pyaudio.get_device_info_by_host_api_device_index(0, int(regex))
        regex = re.compile(regex, re.IGNORECASE)
        info = self.pyaudio.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        for i in range (0, numdevices):
            devinfo = self.pyaudio.get_device_info_by_host_api_device_index(0, i)
            if regex.match(devinfo['name']) \
                    and devinfo['maxInputChannels'] >= min_input_channels \
                    and devinfo['maxOutputChannels'] >= min_output_channels:
                return devinfo
        return None

    def list_devices(self):
        info = self.pyaudio.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        print(f'{numdevices} PyAudio devices: (input/output channels)')
        for i in range (0, numdevices):
            devinfo = self.pyaudio.get_device_info_by_host_api_device_index(0, i)
            print(f'  {i} - "{devinfo["name"]}" ({devinfo["maxInputChannels"]}/{devinfo["maxOutputChannels"]})')

if __name__ == "__main__":
    a = Audio()
    a.list_devices()