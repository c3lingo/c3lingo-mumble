#!/usr/bin/env python3
"""Pass input directly to output.

See https://www.assembla.com/spaces/portaudio/subversion/source/HEAD/portaudio/trunk/test/patest_wire.c

"""
import argparse
import pymumble_py3
import queue
import threading

import sys

import numpy as np

import time

samplerate = pymumble_py3.constants.PYMUMBLE_SAMPLERATE
blocksize = 16
buffersize = 4096


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('-i', '--input-device', type=int_or_str,
                    help='input device ID or substring')
parser.add_argument('-o', '--output-device', type=int_or_str,
                    help='output device ID or substring')
parser.add_argument('-L', '--list-devices', action='store_true',
                    help='show list of audio devices and exit')
parser.add_argument('-c', '--channel', type=int, default=2,
                    help='number of channels')
parser.add_argument('-t', '--dtype', help='audio data type')
parser.add_argument('-l', '--latency', type=float, help='latency in seconds')
args = parser.parse_args()

q = queue.Queue(maxsize=100000)
event = threading.Event()

try:
    # import sounddevice as sd

    # if args.list_devices:
    #     print(sd.query_devices())
    #     parser.exit(0)


    # def play_callback(outdata, frames, time, status):
    #     assert frames == blocksize
    #     if status.output_underflow:
    #         print('Output underflow: increase blocksize?', file=sys.stderr)
    #         raise sd.CallbackAbort
    #     assert not status
    #     try:
    #         data = q.get_nowait()
    #     except queue.Empty:
    #         print('Buffer is empty: increase buffersize?', file=sys.stderr)
    #         raise sd.CallbackAbort
    #     if len(data) < len(outdata):
    #         outdata[:len(data)] = data
    #         outdata[len(data):] = b'\x00' * (len(outdata) - len(data))
    #         raise sd.CallbackStop
    #     else:
    #         outdata[:] = data


    # # def rec_callback(data, frames, time, status):
    # def rec_callback(indata: np.ndarray, frames: int, time, status: sd.CallbackFlags):
    #     # print(indata[:, args.channel-1].shape)
    #     # print(type(frames))
    #     # print(time)
    #     # print(type(status))
    #     """This is called (from a separate thread) for each audio block."""
    #     if status:
    #         print(status, file=sys.stderr)
    #     q.put(indata[:, args.channel - 1].tobytes())


    # q = queue.Queue()

    with sd.InputStream(
            samplerate=samplerate,
            device="Dante Virtual Soundcard, ASIO",
            channels=8,
            callback=rec_callback,
            blocksize=blocksize,
            dtype='int16'):
        time.sleep(0.2)
        stream = sd.RawOutputStream(
            samplerate=samplerate,
            blocksize=blocksize,
            device=3,
            channels=2,
            dtype='int16',
            callback=play_callback,
            finished_callback=event.set)

        with stream:
            # timeout = args.blocksize * args.buffersize / f.samplerate
            # while data:
            #     data = f.buffer_read(args.blocksize, ctype='float')
            #     q.put(data, timeout=timeout)
            # event.wait()  # Wait until playback is finished
            print('#' * 80)
            print('press Enter to stop the stream')
            print('#' * 80)
            input()
        # while True:
        #     data = q.get()

            # abot.sound_output.add_sound(data)
            # time.sleep(0.1)
    # with sd.Stream(device=(args.input_device, args.output_device),
    #                samplerate=args.samplerate, blocksize=args.blocksize,
    #                dtype=args.dtype, latency=args.latency,
    #                channels=args.channels, callback=callback):
    #     print('#' * 80)
    #     print('press Return to quit')
    #     print('#' * 80)
    #     input()

except KeyboardInterrupt:
    parser.exit('\nInterrupted by user')
except queue.Full:
    # A timeout occured, i.e. there was an error in the callback
    parser.exit(1)
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))

try:
    import sounddevice as sd
    import soundfile as sf

    with sf.SoundFile(args.filename) as f:
        for _ in range(args.buffersize):
            data = f.buffer_read(args.blocksize, ctype='float')
            if not data:
                break
            q.put_nowait(data)  # Pre-fill queue

        stream = sd.RawOutputStream(
            samplerate=f.samplerate, blocksize=args.blocksize,
            device=args.device, channels=f.channels, dtype='float32',
            callback=rec_callback, finished_callback=event.set)
        with stream:
            timeout = args.blocksize * args.buffersize / f.samplerate
            while data:
                data = f.buffer_read(args.blocksize, ctype='float')
                q.put(data, timeout=timeout)
            event.wait()  # Wait until playback is finished
except KeyboardInterrupt:
    parser.exit('\nInterrupted by user')

except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))
