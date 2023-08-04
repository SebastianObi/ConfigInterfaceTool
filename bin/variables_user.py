#!/usr/bin/env python3
##############################################################################################################
#
# Copyright (c) 2022 Sebastian Obele  /  obele.eu
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# This software uses the following software-parts:
# six  /  Copyright (c) 2010-2020 Benjamin Peterson  /  https://github.com/benjaminp/six  /  MIT License
# ConfigObj 5  /  Copyright (C) 2005-2014  /  https://github.com/DiffSK/configobj  /  BSD License
# aiohttp  /  Copyright (c) aio-libs contributors  /  https://github.com/aio-libs/aiohttp  /  Apache 2 license
# aiohttp_basicauth  /  Copyright (c) aio-libs contributors  /  https://github.com/romis2012/aiohttp-basicauth  /  Apache 2 license
# flask  /    /  https://flask.palletsprojects.com/en/2.1.x/  /  
# flask_httpauth  /  Copyright (c) 2013 Miguel Grinberg  /  https://github.com/miguelgrinberg/Flask-HTTPAuth  /  MIT License
# gunicorn  /  2009-2015 (c) Paul J. Davis <paul.joseph.davis@gmail.com>  /  https://github.com/benoitc/gunicorn /  
# Reticulum, LXMF, NomadNet  /  Copyright (c) 2016-2022 Mark Qvist  /  unsigned.io  /  MIT License
#
##############################################################################################################


##############################################################################################################
# Include


#### System ####
import sys
import os
import time
import argparse
import platform

#### Config ####
import configparser

#### Variables ####
from collections import defaultdict

#### Files ####
import glob

#### Regex ####
import re

#### External process ####
import subprocess
import socket



##############################################################################################################
# Class


class variables_user_class:
    config = None
    data = defaultdict(dict)
    prefix = ""


    def cmd(self, cmd, default="", timeout=5):
        if cmd == "":
            return default
        try:
            result = subprocess.run(cmd, capture_output=True, shell=True, text=True, timeout=timeout)
            if result.returncode == 0:
                return re.sub(r'^\s+|\s+$', '', result.stdout)
        except:
            None
        return default


    def file(self, file, default=""):
        if file == "":
            return default
        try:
            file_handler = open(file)
            file_string = file_handler.read()
            file_handler.close()
            return re.sub(r'^\s+|\s+$', '', file_string)
        except:
            None
        return default


    def build(self):
        self.data = defaultdict(dict)

        self.data["require"] = ""

        return True


    def add(self, config, sections):
        if sections == "": return False

        if isinstance(config, str):
            self.data[sections] = config
        else:
            sections = sections.replace(",", ";")
            sections = sections.split(";")
            for section in sections:
                section = section.strip()
                if not config.has_section(section): continue
                for (key, val) in config.items(section):
                    self.data[section+"_"+key] = val

        return True


    def config_get(self):
        return True


    def data_get(self, receive_json, send_json):
        if not "data" in receive_json: return True

        if self.prefix in receive_json["data"]:
            self.build()
            for key in self.data:
                send_json["data"][self.prefix + key] = self.data[key]
            return True

        return True


    def data_set(self, receive_json, send_json):
        return True


    def require(self, config):
        if config != "":
            if re.match(r'([^\s(]+)(\s+)?(==|!=)(\s+)?[\'\"]?([^\s\'\")]+)[\'\"]?', config):
                config = re.sub(r' && ', r' and ', config)
                config = re.sub(r' \|\| ', r' or ', config)
                config = re.sub(r'([^\s(]+)(\s+)?(==|!=)(\s+)?[\'\"]?([^\s\'\")]+)[\'\"]?', r'self.data["\1"] \3 "\5"', config)
                try:
                    if eval(config):
                        return True
                    else:
                        return False
                except:
                    return False
            else:
                config = config.lower()
                config = config.replace(" ", ";")
                config = config.replace(",", ";")
                config = config.split(";")
                for x in config:
                    x = x.strip()
                    if x.startswith("!"):
                        x = x[1:]
                        if x in self.data["require"]: return False
                    else:
                        if x not in self.data["require"]: return False
        return True


    def prefix_set(self, prefix):
        self.prefix = prefix


    def __init__(self, config=None):
        self.config = config
        return


    def __del__(self):
        return
