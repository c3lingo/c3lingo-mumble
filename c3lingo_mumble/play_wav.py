#!/usr/bin/env python3
import audioop
import logging
import math
import sys
import time
import wave

from c3lingo_mumble.config import Config
import pymumble_py3


def dBFS(value):
    if value < 1:
        value = 1
    return 20 * math.log10(value / 32767) + 3


def volume(buffer):
    return dBFS(audioop.rms(buffer, 2))


def play_wav(server_args, channelname, file, level):
    mumble = pymumble_py3.Mumble(**server_args)
    mumble.set_receive_sound(True)
    mumble.start()
    mumble.is_ready()
    log = logging.getLogger('play_wav')

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
                    v = volume(data)
                    log.debug(f'Seconds to send: {mumble.sound_output.get_buffer_size():5.1f}s, volume: {v:5.1f} dbFS')
                    if v > level:
                        mumble.sound_output.add_sound(data)
                        time.sleep(mumble.sound_output.get_buffer_size() * 0.9)
                    else:
                        log.debug(f'Skipping chunk because volume {v:5.1f} dBFS is below {level:3.0f} dBFS')
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
                        'loop': True,
                        'level': -999
                    })
    c = config.get_config()
    for k in ('file', 'channel'):
        if k not in c or c[k] is None:
            print('Missing required parameter --{}'.format(k))
            sys.exit(64)
    for k in ('host',):
        if k not in c['mumble-server'] or c['mumble-server'][k] is None:
            print('Missing required parameter --{}'.format(k))
            sys.exit(64)
    lh = logging.StreamHandler(stream=sys.stderr)
    lh.setLevel(logging.DEBUG if c['mumble-server']['debug'] else logging.INFO)
    lh.setFormatter(logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s'))
    logging.root.addHandler(lh)
    log = logging.getLogger('play_wav')
    log.setLevel(logging.INFO)
    log.info(f"Playing \"c['file']\" on channel \"c['channel']\" at c['mumble-server']['host']")
    try:
        play_wav(c['mumble-server'], c['channel'], c['file'], c['level'])
    except Exception as e:
        print(f'Unable to play file: {e.__class__.__name__}: {e}', file=sys.stderr)

