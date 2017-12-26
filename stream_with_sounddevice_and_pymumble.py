#!/usr/bin/env python3
"""Create a recording with arbitrary duration.

"""
import argparse
import tempfile
import queue
import sys
from typing import Union
import time
import numpy as np
import pymumble_py3 as pymumble

samplerate = pymumble.constants.PYMUMBLE_SAMPLERATE

def int_or_str(text) -> Union[str, int]:
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
parser.add_argument(
    '-d', '--device', type=int_or_str,
    help='input device (numeric ID or substring)')
# parser.add_argument(
#     '-r', '--samplerate', type=int, help='sampling rate')
parser.add_argument(
    '-c', '--channel', type=int, default=1, help='channel to record (1-indexed)')
# parser.add_argument(
#     '-t', '--subtype', type=str, help='sound file subtype (e.g. "PCM_24")')
args = parser.parse_args()

thread_running = True

try:
    import sounddevice as sd
    # import soundfile as sf

    if args.list_devices:
        print(sd.query_devices())
        parser.exit(0)

    q = queue.Queue()

    host = 'mumble.c3lingo.org'
    user = 'abot3'

    abot = pymumble.Mumble(host, user)

    abot.set_application_string("c3lingo (%s)" % 0.1)
    abot.set_codec_profile('audio')
    abot.start()
    abot.set_bandwidth(90000)
    abot.is_ready()
    print("abot is ready!")
    # abot.sound_output.add_sound(frames)

    def callback(indata: np.ndarray, frames: int, time, status: sd.CallbackFlags):
        # print(indata[:, args.channel-1].shape)
        # print(type(frames))
        # print(time)
        # print(type(status))
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        # q.put(indata.copy())
        q.put(indata[:, args.channel-1].tobytes())

    with sd.InputStream(samplerate=samplerate,
                        device=args.device,
                        channels=2,
                        callback=callback,
                        blocksize=256,
                        dtype='int16'):
        print('#' * 80)
        print('press Ctrl+C to stop the stream')
        print('#' * 80)
        while thread_running:
            data = q.get()
            abot.sound_output.add_sound(data)
            # time.sleep(0.1)

except KeyboardInterrupt:
    print('\nRecording finished: ' + repr(args.filename))
    parser.exit(0)
except Exception as e:
    raise e
    parser.exit(type(e).__name__ + ': ' + str(e))