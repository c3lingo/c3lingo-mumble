#!/usr/bin/env python3

"""
Send one or more channels of audio recording from PyAudio sources to
selected Mumble channels.
"""
import argparse
import audioop
import math
import os
import re
import struct
import sys
import threading
import time
import wave

import pymumble_py3
import yaml

from c3lingo_mumble.stdchannel_redirected import stdchannel_redirected


class AppError(Exception):
    pass


def dBFS(value):
    if value < 1:
        value = 1
    return 20 * math.log10(value / 32767) + 3


def volume(buffer):
    return dBFS(audioop.rms(buffer, 2))


class MumbleSender:
    def __init__(self, server_args, channelname, level=-999):
        self.server_args = server_args
        self.channel = channelname
        self.level = level
        self.count = 0

        mumble = pymumble_py3.Mumble(**server_args)
        self.mumble = mumble
        mumble.set_receive_sound(True)
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
        v = volume(data)
        if self.mumble.sound_output is not None and v > self.level:
            self.mumble.sound_output.add_sound(data)
        self.count += 1


class StdinSender:
    def __init__(self, config):
        self.config = config
        self.mumbles = {}
        self.maxchannels = len(config)
        for (index, params) in enumerate(self.config):
            level = params['level'] if 'level' in params else -999
            self.mumbles[index] = MumbleSender(params['server'], params['channel'], level)
            print(f'Connected {index} to {params["server"]["host"]}/{params["channel"]}, minimum level {level}')

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
        while True:
            b = sys.stdin.buffer.read(480 * 2 * self.maxchannels)
            if not b:
                print('End of source file')
                break
            streams = self.split_channels(b, self.maxchannels)
            for index in range(len(self.config)):
                self.mumbles[index].send(streams[index])
            time.sleep(0.005)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Send one or more PyAudio sources to a mumble server')
    parser.add_argument('-f', '--file')
    c = parser.parse_args()
    if not c.file:
        print('usage: usage: send_pulseaudio -f <configfile>', file=sys.stderr)
        sys.exit(64)
    try:
        with open(c.file, 'r') as file:
            config = yaml.safe_load(file)
        if 'channels' not in config:
            print('The config file must specify a channel mapping under "channels"')
            sys.exit(64)
        input = StdinSender(config['channels'])
        input.start()
        input.thread.join()
    except AppError as e:
        print(f'Unable to send audio: {e.__class__.__name__}: {e}', file=sys.stderr)
