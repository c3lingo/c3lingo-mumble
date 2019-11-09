#!/usr/bin/env python

import argparse
import sys

import yaml


class Config:
    def __init__(self, defaults={}, description=None):
        self.config = {}
        self.defaults = defaults
        self.description = description

    def add_config_args(self, d):
        for (k, v) in d.items():
            if isinstance(v, dict):
                self.add_config_args(v)
            else:
                self.parser.add_argument('--{}'.format(k))

    def update_config(self, config, args):
        for (k, v) in config.items():
            if isinstance(v, dict):
                self.update_config(v, args)
            elif k in args and args[k] is not None:
                config[k] = args[k]

    def load_yaml(self, file):
        with open(file, 'r') as fd:
            y = yaml.safe_load(fd)
        self.update_config(self.config, y)

    def get_config(self, args=sys.argv[1:]):
        self.parser = argparse.ArgumentParser(description=self.description)
        self.parser.add_argument('-c', '--config')
        self.add_config_args(self.defaults)
        c = self.parser.parse_args(args)
        self.config = dict(self.defaults)
        if c.config:
            self.load_yaml(c.config)
        self.update_config(self.config, dict(vars(c).items()))
        return self.config
