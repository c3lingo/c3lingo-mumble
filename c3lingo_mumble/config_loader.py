import json


def load_config(config_path):

    with open(config_path, 'r') as config_json:
        return json.load(config_json)