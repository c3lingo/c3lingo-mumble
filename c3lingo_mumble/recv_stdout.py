#!/usr/bin/python3

import os
import random
import string
import sys
import time
import threading

from array import array
from datetime import datetime, timedelta

from pymumble_py3 import Mumble
from pymumble_py3.callbacks import PYMUMBLE_CLBK_SOUNDRECEIVED
from pymumble_py3.constants import PYMUMBLE_CONN_STATE_NOT_CONNECTED


class MumbleReceiver:
    def __init__(self, server, channel, file, nick='recv-{r}@{channel}', debug=False):
        r = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        self.channelname = channel
        self.nick = nick.format(r=r, channel=channel)
        self.mumble = Mumble(server, self.nick, password='somepassword',
                             debug=debug)
        self.mumble.set_application_string(
            'Receiver for Channel {}'.format(channel))
        if file:
            self.fd = open(file, "wb", 0o644);
        else:
            self.fd = os.fdopen(sys.stdout.fileno(), "wb", closefd=False)

        self.rate = 48000
        self.interval = .02 # 20ms of samples

        self.mumble.set_receive_sound(1)
        self.mumble.start()
        self.mumble.is_ready()

        self.channel = self.mumble.channels.find_by_name(self.channelname)
        self.channel.move_in()

        self.thread = None
        self.start()

    def start(self):
        self.thread = threading.Thread(target=self.send, daemon=True)
        self.thread.start()

    def clip(self, val):
        return -32768 if val < -32768 else 32767 if val > 32767 else val

    def send(self):
        ts = time.time() - self.interval
        while True:
            start = time.time()
            buffer = array("h", [0]*int(self.interval*self.rate))
            for user in self.channel.get_users():
                sound = user.sound.get_sound(self.interval)
                if not sound:
                    continue
                samples = array("h")
                samples.frombytes(sound.pcm)
                if sys.byteorder == 'big':
                    samples.byteswap()
                for i in range(0, len(samples)):
                    buffer[i] = self.clip(buffer[i] + samples[i])
            if sys.byteorder == 'big':
                buffer.byteswap()
            self.fd.write(buffer.tobytes())
            wait = self.interval * 0.9 - (time.time() - start)
            if wait > 0:
                time.sleep(wait)
            while time.time() < ts: # spin until time is reached
                pass


def main():
    if len(sys.argv) < 3:
        print(f"usage: {os.path.basename(sys.argv[0])} server channel [file]", file=sys.stderr)
        sys.exit(64)
    (ignore, server, channel, *file) = sys.argv
    client = MumbleReceiver(server, channel, file)
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
