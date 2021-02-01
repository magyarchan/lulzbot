#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from pyhocon import ConfigFactory

class Config:
    def __init__(self, config = "dev.conf"):
        configPath = f'conf/{config}'
        self.conf = ConfigFactory.parse_file(configPath)

    def getInstance(self):
        return self.conf

    def debug(self):
        print(self.conf)

    def getString(self, key):
        return self.conf.get_string(key)

    def getInt(self, key):
        return self.conf.get_int(key)

    def getBoolean(self, key):
        return self.conf.get_bool(key)

