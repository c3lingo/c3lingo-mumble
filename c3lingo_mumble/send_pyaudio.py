#!/usr/bin/env python3

"""
Send one or more channels of audio recording from PyAudio sources to
selected Mumble channels.
"""
import argparse
import struct
import sys
import threading
import time

import pymumble_py3
import yaml

from c3lingo_mumble.audio import Audio


class AppError(Exception):
    pass


class MumbleSender:
    def __init__(self, server_args, channelname):
        self.server_args = server_args
        self.channel = channelname
        self.count = 0

        mumble = pymumble_py3.Mumble(**server_args)
        self.mumble = mumble
        mumble.start()
        mumble.is_ready()

        if not mumble.is_alive():
            raise AppError(f'Connection to "{server_args["host"]}" failed')
        channel = mumble.channels.find_by_name(channelname)
        channel.move_in()

        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            if mumble.my_channel() == channel:
                break
            time.sleep(.1)
        if mumble.my_channel() != channel:
            raise AppError(f'Unable to move to channel "{channelname}"')

    def send(self, data):
        self.mumble.sound_output.add_sound(data)
        self.count += 1


class PyAudioSender:
    def __init__(self, name, config, audio):
        self.name = name
        self.config = config
        self.audio = audio
        self.mumbles = {}
        self.devinfo = audio.get_devinfo(source)
        if not self.devinfo:
            raise AppError(f'Unable to find device matching "{source}"')
        self.maxchannels = self.devinfo['maxInputChannels']
        for (index, params) in config.items():
            if index > self.devinfo['maxInputChannels'] - 1:
                raise AppError(
                    f'Channel index {index} is too large for device "{self.devinfo["name"]}"')
            self.mumbles[index] = MumbleSender(params['server'], params['channel'])
            print(f'Connected {self.devinfo["name"]}/{index} to {params["server"]["host"]}/{params["channel"]}')

    def start(self):
        self.thread = threading.Thread(target=self.send, daemon=True)
        self.thread.start()

    @staticmethod
    def split_channels(multi, nchannels):
        singles = []
        for i in range(0, nchannels):
            singles.append(b'')
        for samples in struct.iter_unpack(f'<{nchannels}h', multi):
            for i in range(0, nchannels):
                singles[i] += struct.pack('<h', samples[i])
        return singles

    def send(self):
        stream = self.audio.pyaudio.open(format=self.audio.pyaudio.get_format_from_width(2),
                        channels=self.maxchannels,
                        rate=48000,
                        input_device_index=self.devinfo['index'],
                        input=True)
        while True:
            streams = self.split_channels(stream.read(480, exception_on_overflow=False), self.maxchannels)
            for index in self.config.keys():
                self.mumbles[index].send(streams[index])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Send one or more PyAudio sources to a mumble server')
    parser.add_argument('-f', '--file')
    parser.add_argument('-l', '--list', action='store_true')
    c = parser.parse_args()
    if c.list:
        audio = Audio()
        audio.list_devices()
        sys.exit(0)
    if not c.file:
        print('usage: usage: send_pulseaudio -f <configfile>', file=sys.stderr)
        sys.exit(64)
    try:
        with open(c.file, 'r') as file:
            config = yaml.safe_load(file)
        audio = Audio()
        inputs = []
        for (source, params) in config['sources'].items():
            inputs.append(PyAudioSender(source, params, audio))
        for input in inputs:
            input.start()
        while True:
            # counters = []
            # for mumble in input.mumbles.values():
            #     counters.append(mumble.count)
            # print(f'    {counters}')
            time.sleep(1)
    except AppError as e:
        print(f'Unable to send audio: {e.__class__.__name__}: {e}', file=sys.stderr)
