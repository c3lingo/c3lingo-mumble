"""
Contains a class to stream audio from an Audio input to a Mumble
channel.
"""
import logging
import os
import pymumble_py3 as pymumble
import queue
import sounddevice

import numpy as np

import sys

from c3lingo_mumble import asio_singleton

LOG = logging.getLogger("fuuuu")
LOG.setLevel(logging.INFO)

class ConfigurationError(Exception):
    pass


class MumbleMapping(object):

    def __init__(self, audio_input, audio_channel, mumble_username, mumble_channel, mumble_cert, mumble_key):
        self.mumble_cert = self.check_cert(mumble_cert)
        self.mumble_key = self.check_cert(mumble_key)
        self.mumble_channel = self.check_mumble_channel(mumble_channel)
        self.mumble_username = self.check_mumble_username(mumble_username)
        self.audio_channel = self.check_audio_channel(audio_channel)
        self.audio_input = self.check_audio_input(audio_input)

    @staticmethod
    def check_cert(mumble_cert):
        if isinstance(mumble_cert, str):
            if os.path.isfile(mumble_cert):
                return mumble_cert
            else:
                raise ConfigurationError("Could not find Mumble Certificate at {}.".format(mumble_cert))
        else:
            raise ConfigurationError("Mumble Certificate is not an instance of str.")

    @staticmethod
    def check_mumble_channel(mumble_channel):
        if isinstance(mumble_channel, str):
            return mumble_channel
        else:
            raise ConfigurationError("Mumble channel is not an instance of str.")

    @staticmethod
    def check_mumble_username(mumble_username):
        if isinstance(mumble_username, str):
            return mumble_username
        else:
            raise ConfigurationError("Mumble User Name is not an instance of str.")

    @staticmethod
    def check_audio_channel(audio_channel):
        try:
            audio_channel_int = int(audio_channel)
            if audio_channel_int > 0:
                return audio_channel_int
            else:
                raise ConfigurationError("Audio Channel is 1-indexed. Zero or negative values are not valid.")
        except ValueError as e:
            raise ConfigurationError("Audio Channel could not be converted to an int.")

    @staticmethod
    def check_audio_input(audio_input):
        try:
            if sounddevice.query_devices(str(audio_input)):
                return audio_input
            else:
                raise ConfigurationError("Audio Input could not be found with the sounddevice library.\n{}".format(sounddevice.query_devices("lalalal")))
        except ValueError as e:
            raise ConfigurationError("Audio Input was a weird object. Please fix that. For reference: {}".format(e))


class MumbleClient(object):

    @staticmethod
    def check_mapping(mapping) -> MumbleMapping:
        return MumbleMapping(mapping["audio_input"],
                             mapping["audio_channel"],
                             mapping["mumble_user"],
                             mapping["mumble_channel"],
                             mapping["mumble_cert"],
                             mapping["mumble_key"]
                             )

    def __init__(self, hostname, port, mapping, input_stream: asio_singleton.AsioSingleton):
        self.mapping = self.check_mapping(mapping)
        del mapping
        self.port = port
        self.hostname = hostname

        self.audio_queue = queue.Queue()
        self.thread_comm_queue = queue.Queue()

        self.mumble_conn_thread = pymumble.Mumble(host=self.hostname,
                                                  user=self.mapping.mumble_username,
                                                  certfile=self.mapping.mumble_cert,
                                                  keyfile=self.mapping.mumble_key,
                                                  debug=False)

        self.mumble_conn_thread._set_ident()

        self.mumble_conn_thread.set_application_string("c3lingo (%s)" % 0.1)
        self.mumble_conn_thread.set_codec_profile('audio')
        self.mumble_ready = False


        # self.audio_input_thread = sounddevice.InputStream(
        #     samplerate=48000,  # PyMumble wills it.
        #     device=self.mapping.audio_input,
        #     channels=sounddevice.query_devices(self.mapping.audio_input)["max_input_channels"],  # TODO: Move to configuration
        #     callback=self.construct_audio_callback(),
        #     blocksize=128,  # TODO: Move to configuration
        #     dtype='int16')

        self.audio_input_proxy = input_stream

        self.audio_input_proxy.initialize(self.mapping.audio_input)
        self.audio_input_proxy.add_listener(self.mapping.audio_channel, self)

        # abot = pymumble.Mumble(host, user)
        #
        # abot.set_application_string("c3lingo (%s)" % 0.1)
        # abot.set_codec_profile('audio')
        # abot.start()
        # abot.set_bandwidth(90000)

    # def construct_audio_callback(self):
    #     def callback(indata: np.ndarray, frames: int, time, status: sounddevice.CallbackFlags):
    #         """This is called (from a separate thread) for each audio block."""
    #         # LOG.error("Test")
    #         if status:
    #             print(status, file=sys.stderr)
    #             self.thread_comm_queue.put()
    #         # q.put(indata.copy())
    #         # self.audio_queue.put(indata[:, self.mapping.audio_channel - 1].tobytes())
    #         if self.mumble_ready:
    #             self.mumble_conn_thread.sound_output.add_sound(indata[:, self.mapping.audio_channel - 1].tobytes())
    #         del indata
    #
    #     return callback

    def start(self):
        LOG.error("starting threads")

        self.mumble_conn_thread.start()
        LOG.error("mumble thread started")

        self.wait_for_mumble_ready()
        LOG.error("mumble ready")

        LOG.error("done starting threads")
        return self.thread_comm_queue

    def wait_for_mumble_ready(self):
        self.mumble_conn_thread.is_ready()

        self.mumble_conn_thread.set_bandwidth(64000)

        (self.mumble_conn_thread.channels
            .find_by_name(self.mapping.mumble_channel)
            .move_in(self.mumble_conn_thread.users.myself_session))

        self.mumble_ready = True

