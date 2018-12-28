import logging
import time

from queue import Empty
from . import config_loader
from .mumble_client import MumbleClient
from . import asio_singleton

input_stream = asio_singleton.input_stream


def handle_event(event, instance):
    if event.type == "Disconnected" or "Stopped":
        instance.run()
        instance.retries += 1


def main(config_path):

    config = config_loader.load_config(config_path)

    instances = []
    retries = []
    queues = []

    server = config["server"]
    mappings = config["mappings"]

    # for x in range(0, 7):
    for mapping in mappings:
        instance = MumbleClient(
            server["hostname"],
            server["port"],
            mapping,
            input_stream)

        # setattr(instance, "retries", 0)
        instance.retries = 0
        instances.append(instance)

    for instance in instances:
        # something happens!
        instance_queue = instance.start()
        queues.append((instance_queue, instance))

    while True:
        for queue, instance in queues:
            try:
                handle_event(queue.get(False), instance)
            except Empty:
                time.sleep(0.01)

if __name__ == "__main__":
    main("config.json")