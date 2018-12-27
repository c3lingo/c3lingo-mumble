import numpy as np
import sounddevice

import sys
import logging

LOG = logging.getLogger("bar")

class AsioSingleton(object):

    def __init__(self):
        self.listeners = {}
        self.number_of_channels = 0
        self.audio_input_thread = None
        self.initialized = False

    def initialize(self, audio_input):
        if self.initialized:
            return

        self.number_of_channels = sounddevice.query_devices(audio_input)["max_input_channels"]

        self.audio_input_thread = sounddevice.InputStream(
            samplerate=48000,  # PyMumble wills it.
            device=audio_input,
            channels=self.number_of_channels,
            callback=self.inputstream_callback,
            blocksize=32,  # TODO: Move to configuration
            dtype='int16')
        self.audio_input_thread.start()
        self.initialized = True

    def add_listener(self, channel, listener):
        self.listeners[channel] = listener

    def inputstream_callback(self, indata: np.ndarray, frames: int, time, status: sounddevice.CallbackFlags):
        """This is called (from a separate thread) for each audio block."""

        # if status:
        #     print(status, file=sys.stderr)

        for channel, mumble_client in self.listeners.items():

            if mumble_client.mumble_ready:
                mumble_client.mumble_conn_thread.sound_output.add_sound(indata[:, channel - 1].tobytes())
            # else:
            #     print('.', file=sys.stderr, end='')
        del indata


input_stream = AsioSingleton()
