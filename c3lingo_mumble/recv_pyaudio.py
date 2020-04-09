#!/usr/bin/python3

import os
import random
import string
import sys
import time
import threading

import pyaudio

from array import array

from pymumble_py3 import Mumble

from c3lingo_mumble.audio import Audio


class MumbleReceiver:
    def __init__(self, server, channel, dev, nick='recv-{r}@{channel}', use_cb=False, debug=False):
        r = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        self.channelname = channel
        self.nick = nick.format(r=r, channel=channel)
        self.mumble = Mumble(server, self.nick, password='somepassword',
                             debug=debug)
        self.mumble.set_application_string(
            'Receiver for Channel {}'.format(channel))
        audio = Audio()
        devinfo = audio.get_devinfo(dev, min_input_channels=0)
        if not devinfo:
            print(f"Unable to find output device \"{dev}\".", file=sys.stderr)
            print(f"use \"python -m c3lingo_mumble.audio\" to get a list of devices", file=sys.stderr)
            sys.exit(1)

        self.rate = 48000
        self.interval = .02  # 20ms of samples

        self.mumble.set_receive_sound(1)
        self.mumble.start()
        self.mumble.is_ready()

        self.channel = self.mumble.channels.find_by_name(self.channelname)
        self.channel.move_in()

        self.thread = None
        if use_cb:
            callback = self.pyaudio_send
        else:
            callback = None
        self.stream = audio.pyaudio.open(format=audio.pyaudio.get_format_from_width(2),
                                         channels=1,
                                         rate=48000,
                                         output_device_index=devinfo['index'],
                                         output=True,
                                         stream_callback=callback)
        if use_cb:
            self.stream.start_stream()
        else:
            self.start()

    def start(self):
        self.thread = threading.Thread(target=self.send, daemon=True)
        self.thread.start()

    def clip(self, val):
        return -32768 if val < -32768 else 32767 if val > 32767 else val

    def get_audio(self):
        buffer = array("h", [0] * int(self.interval * self.rate))
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
        return buffer.tobytes()

    def send(self):
        ts = time.time() - self.interval
        while True:
            start = time.time()
            self.stream.write(self.get_audio())
            wait = self.interval * 0.9 - (time.time() - start)
            if wait > 0:
                time.sleep(wait)
            while time.time() < ts:  # spin until time is reached
                pass

    def pyaudio_send(self, in_data, frame_count, time_info, status):
        data = self.get_audio()
        return (data, pyaudio.paContinue)


def main():
    if len(sys.argv) < 3:
        print(f"usage: {os.path.basename(sys.argv[0])} server channel portaudio-device", file=sys.stderr)
        sys.exit(64)
    (ignore, server, channel, dev) = sys.argv
    client = MumbleReceiver(server, channel, dev)
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
