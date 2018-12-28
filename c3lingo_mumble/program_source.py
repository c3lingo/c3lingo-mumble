import sys
import logging
import numpy as np

LOG = logging.getLogger("ProgramSource")

class BadConfigurationError(Exception):
    pass

# class Program(object):
#     @classmethod
#     def from_dict(cls, dict_object):
#         try:
#             return cls(dict_object["invocation_string"],
#                        dict_object["number_of_channels"])
#         except:
#             raise BadConfigurationError()

#     def __init__(self, invocation_string, number_of_channels):
#         self.invocation_string = invocation_string
#         self.number_of_channels = number_of_channels

class ProgramSource(object):

    def __init__(self):
        self.initialized = False

    def initialize(self, invocation_string, channels):
        if self.initialized:
            return
        

        # self.number_of_channels = sounddevice.query_devices(audio_input)["max_input_channels"]

        # self.audio_input_thread = sounddevice.InputStream(
        #     samplerate=48000,  # PyMumble wills it.
        #     device=audio_input,
        #     channels=self.number_of_channels,
        #     callback=self.inputstream_callback,
        #     blocksize=32,  # TODO: Move to configuration
        #     dtype='int16')
        # self.audio_input_thread.start()
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
