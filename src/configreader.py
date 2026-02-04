#! /usr/bin/env python
#coding=utf-8

import configparser
import os

class ConfigReader(object):
    
    def __init__(self):
        self.mConfig = configparser.RawConfigParser()
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.mConfig.read(os.path.join(root_dir, 'settings.cfg'))
    
    def get(self, section, prop):
        return True if self.mConfig.get(section, prop) == 'True' else False
