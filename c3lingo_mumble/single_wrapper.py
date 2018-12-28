import logging
import time
import sys
import os
from queue import Empty

from c3lingo_mumble.mumble_client import MumbleClient

host = os.environ['HOST']
port = os.environ['PORT']
channel = os.environ['MUMBLE_CHANNEL']
user = os.environ['MUMBLE_USER']
cert = os.environ['MUMBLE_CERT']
key = os.environ['MUMBLE_KEY']


def handle_event(event, instance):
    if event.type == "Disconnected" or "Stopped":
        instance.run()
        instance.retries += 1


def main():
    
    instance = MumbleClient(host, int(port), channel, user, cert, key, sys.stdin)

    instance.retries = 0

    # something happens!
    instance_queue = instance.start()

    while True:
        try:
            handle_event(instance_queue.get(False), instance)
        except Empty:
            time.sleep(0.01)

if __name__ == "__main__":
    main()