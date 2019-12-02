#!/usr/bin/env python3

"""
Create many mumble clients listening to a channel. This can be used as a load
test tool.

usage: python -m c3lingo_mumble.manylisteners localhost client-a 300 100 60
"""
import random
import sys
import time

from c3lingo_mumble.config import Config

from pymumble_py3 import Mumble
from pymumble_py3.callbacks import PYMUMBLE_CLBK_SOUNDRECEIVED
from pymumble_py3.constants import PYMUMBLE_CONN_STATE_NOT_CONNECTED


class MumbleListener:
    def __init__(self, server, nick, channel, debug=False):
        self.nick = nick.format(channel=channel)
        self.mumble = Mumble(server, self.nick, password='somepassword', debug=debug)
        self.mumble.set_application_string('Audio Meter for Channel {}'.format(channel))
        self.mumble.callbacks.set_callback(PYMUMBLE_CLBK_SOUNDRECEIVED, self.sound_received_handler)
        self.mumble.set_receive_sound(1)
        self.mumble.start()
        self.mumble.is_ready()
        if channel is not 'root':
            self.channel = self.mumble.channels.find_by_name(channel)
            self.channel.move_in()

    def sound_received_handler(self, user, sound):
        pass


def get_channel_list(server):
    mumble = Mumble(server, 'random_user', password='somepassword', debug=False)
    mumble.start()
    mumble.is_ready()
    channels = [c['name'] for c in list(mumble.channels.values())[1:]]
    if mumble.is_alive():
        mumble.connected = PYMUMBLE_CONN_STATE_NOT_CONNECTED
        mumble.control_socket.close()
    return channels


if __name__ == "__main__":
    if len(sys.argv) != 6:
        print('usage: manylisteners server basename ramp_seconds count sustain_seconds')
        sys.exit(64)
    (server, basename, ramp_seconds, count, sustain_seconds) = sys.argv[1:]
    channels = get_channel_list(server)
    print(channels)
    listeners = []

    for i in range(0, int(count)):
        channel = random.choice(channels)
        nick = f'{basename}-{i:05d}'
        print(f'adding {nick}@{server}, channel {channel}')
        listeners.append(MumbleListener(server, nick, channel))
        time.sleep(float(ramp_seconds) / int(count))
    print(f'ramp to {count} listeners completed, sleeping for {sustain_seconds} seconds')
    time.sleep(float(sustain_seconds))