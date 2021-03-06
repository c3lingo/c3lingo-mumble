"""
Contains a class to stream audio from an Audio input to a Mumble
channel.
"""
import os
import sys
import time
import queue
import logging
import threading
import pymumble_py3 as pymumble
from queue import Empty
from threading import Thread
from pymumble_py3.constants import PYMUMBLE_CONN_STATE_CONNECTED, PYMUMBLE_CONN_STATE_NOT_CONNECTED

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


class MumbleClient(object):
    def start_listening(self):
        def thread_func(audio_queue, data_stream):
            while True:
                data = data_stream.read(128)
                audio_queue.put(data)
        
        listener_thread = Thread(target=thread_func, args=(self.audio_queue, self.stream)) 
        listener_thread.start()
        return listener_thread

    def start_streaming(self):
        running = True

        def thread_func(audio_queue, mumble_obj):
            while True:
                try:
                    while True:
                        data = audio_queue.get(False)
                        
                        if self.mumble_ready:
                            mumble_obj.sound_output.add_sound(data)
                        else:
                            del data
            
                except Empty:
                    time.sleep(0.01)

        streamer_thread = Thread(target=thread_func, args=(self.audio_queue, self.mumble_conn_thread)) 
        streamer_thread.start()
        return streamer_thread

    def __init__(self, hostname, port, channel, user, cert, key, stream):
        self.stream = stream
        self.mumble_channel = channel
        self.audio_queue = queue.Queue()
        self.thread_comm_queue = queue.Queue()

        self.mumble_conn_thread = pymumble.Mumble(host=hostname,
                                                  port=port,
                                                  user=user,
                                                  certfile=cert,
                                                  keyfile=key,
                                                  debug=False,
                                                  reconnect=True)

        self.mumble_conn_thread._set_ident()

        self.mumble_conn_thread.set_application_string("c3lingo (%s)" % 0.1)
        self.mumble_conn_thread.set_codec_profile('audio')

    @property
    def mumble_ready(self):
        # lock_acquired = self.mumble_conn_thread.ready_lock.acquire(False)
        # if lock_acquired:
        #     self.mumble_conn_thread.ready_lock.release()
        mumble_connection_status = getattr(self.mumble_conn_thread, "connected", PYMUMBLE_CONN_STATE_NOT_CONNECTED)
        return mumble_connection_status == PYMUMBLE_CONN_STATE_CONNECTED

    def start(self):
        LOG.error("starting threads")

        self.mumble_conn_thread.start()
        LOG.error("mumble thread started")

        self.wait_for_mumble_ready()
        LOG.error("mumble ready")

        self.listener_thread = self.start_listening()
        self.streamer_thread = self.start_streaming()

        LOG.error("done starting threads")
        return self.thread_comm_queue

    def wait_for_mumble_ready(self):
        self.mumble_conn_thread.is_ready()

        self.mumble_conn_thread.set_bandwidth(64000)

        foo = (self.mumble_conn_thread.channels
            .find_by_name(self.mumble_channel))
        foo.move_in(self.mumble_conn_thread.users.myself_session)
