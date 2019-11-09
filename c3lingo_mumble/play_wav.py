#!/usr/bin/env python3

import sys
import time
import wave

from c3lingo_mumble.config import Config
import pymumble_py3


def play_wav(server_args, channelname, file):
    mumble = pymumble_py3.Mumble(**server_args)
    mumble.start()
    mumble.is_ready()

    if not mumble.is_alive():
        raise Exception(f'Connection to "{server_args["host"]}" failed')
    channel = mumble.channels.find_by_name(channelname)
    channel.move_in()

    deadline = time.monotonic() + 2
    while time.monotonic() < deadline:
        if mumble.my_channel() == channel:
            break
        time.sleep(.1)
    if mumble.my_channel() != channel:
        raise Exception(f'Unable to move to channel "{channelname}"')

    try:
        while True:
            with wave.open(file, 'rb') as wf:
                duration = 1.0 * wf.getnframes() / wf.getframerate()
                chunk = int(wf.getframerate() * 0.1)  # 100ms chunks
                start = time.perf_counter()
                data = wf.readframes(chunk)
                while len(data) > 0:
                    mumble.sound_output.add_sound(data)
                    data = wf.readframes(chunk)
            now = time.perf_counter()
            elapsed = now - start
            remaining = duration - elapsed + 1
            if remaining > 0:
                time.sleep(remaining)
    except KeyboardInterrupt:
        mumble.control_socket.close()


if __name__ == "__main__":
    config = Config(description='Send a WAV file to a Mumble server',
                    defaults={
                        'file': None,
                        'mumble-server': {
                            # see pymumble_py3.mumbly.Mumble.__init__
                            'host': None,
                            'port': 64738,
                            'user': 'play_wav',
                            'password': '',
                            'certfile': None,
                            'keyfile': None,
                            'reconnect': False,
                            'tokens': [],
                            'debug': False,
                        },
                        'channel': None,
                        'loop': True
                    })
    c = config.get_config()
    for k in ('file', 'channel'):
        if k not in c:
            print('Missing required parameter --{}'.format(k))
            sys.exit(64)
    for k in ('host',):
        if k not in c['mumble-server']:
            print('Missing required parameter --{}'.format(k))
            sys.exit(64)
    print('Playing \"{}\" on channel \"{}\" at {}'
          .format(c['file'], c['channel'], c['mumble-server']['host']))
    try:
        play_wav(c['mumble-server'], c['channel'], c['file'])
    except Exception as e:
        print(f'Unable to play file: {e.__class__.__name__}: {e}', file=sys.stderr)

