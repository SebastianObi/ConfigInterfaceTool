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
#
##############################################################################################################


##############################################################################################################
# Include


#### System ####
import sys
import os
#import time
import argparse
#import platform

#### Config ####
from vendor.configobj import ConfigObj

#### JSON ####
import json
import pickle


##############################################################################################################
# Globals


#### Global Variables - Configuration ####
NAME = "ConfigEditor"
DESCRIPTION = "Simple command line config editor."
VERSION = "0.0.1 (2022-10-21)"
COPYRIGHT = "(c) 2022 Sebastian Obele  /  obele.eu"
#PATH = os.path.expanduser("~") + "/." + os.path.splitext(os.path.basename(__file__))[0]
#PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.dirname(os.path.abspath(__file__)).rstrip("/bin")


##############################################################################################################
# Config


def config_edit(file, config):
    if not file.startswith("/"): file = PATH + "/" + file
    if not os.path.exists(file):
        panic()

    try:
        config_file = ConfigObj(file, file_error=True, write_empty_values=True, encoding="utf8")
    except:
        panic()

    try:
        config = json.loads(config)
    except:
        panic()

    try:
        for section in config.keys():
            for item in config[section].keys():
                config_file[section][item] = config[section][item]
        config_file.write()
    except:
        panic()
    exit()


##############################################################################################################
# Log


LOG_FORCE    = -1
LOG_CRITICAL = 0
LOG_ERROR    = 1
LOG_WARNING  = 2
LOG_NOTICE   = 3
LOG_INFO     = 4
LOG_VERBOSE  = 5
LOG_DEBUG    = 6
LOG_EXTREME  = 7

LOG_LEVEL         = LOG_NOTICE
LOG_LEVEL_SERVICE = LOG_NOTICE
LOG_TIMEFMT       = "%Y-%m-%d %H:%M:%S"
LOG_MAXSIZE       = 5*1024*1024
LOG_PREFIX        = ""
LOG_SUFFIX        = ""
LOG_FILE          = ""


def log(text, level=3, file=None):
    if not LOG_LEVEL:
        return

    if LOG_LEVEL >= level:
        name = "Unknown"
        if (level == LOG_FORCE):
            name = ""
        if (level == LOG_CRITICAL):
            name = "Critical"
        if (level == LOG_ERROR):
            name = "Error"
        if (level == LOG_WARNING):
            name = "Warning"
        if (level == LOG_NOTICE):
            name = "Notice"
        if (level == LOG_INFO):
            name = "Info"
        if (level == LOG_VERBOSE):
            name = "Verbose"
        if (level == LOG_DEBUG):
            name = "Debug"
        if (level == LOG_EXTREME):
            name = "Extra"

        if not isinstance(text, str):
            text = str(text)

        text = "[" + time.strftime(LOG_TIMEFMT, time.localtime(time.time())) +"] [" + name + "] " + LOG_PREFIX + text + LOG_SUFFIX

        if file == None and LOG_FILE != "":
            file = LOG_FILE

        if file == None:
            print(text)
        else:
            try:
                file_handle = open(file, "a")
                file_handle.write(text + "\n")
                file_handle.close()
                
                if os.path.getsize(file) > LOG_MAXSIZE:
                    file_prev = file + ".1"
                    if os.path.isfile(file_prev):
                        os.unlink(file_prev)
                    os.rename(file, file_prev)
            except:
                return


##############################################################################################################
# System


#### Panic #####
def panic():
    sys.exit(255)


#### Exit #####
def exit():
    sys.exit(0)


##############################################################################################################
# Setup/Start


#### Setup #####
def setup(path_log=None, loglevel=None, service=False):
    global LOG_LEVEL
    global LOG_FILE

    if loglevel is not None:
        LOG_LEVEL = loglevel

    if service:
        LOG_LEVEL = LOG_LEVEL_SERVICE
        if path_log is not None:
            LOG_FILE = path_log
        else:
            LOG_FILE = PATH
        LOG_FILE = LOG_FILE + "/" + NAME + ".log"


#### Start ####
def main():
    try:
        description = NAME + " - " + DESCRIPTION
        parser = argparse.ArgumentParser(description=description)

        parser.add_argument("-pl", "--path_log", action="store", type=str, default=None, help="Path to alternative log directory")
        parser.add_argument("-l", "--loglevel", action="store", type=int, default=LOG_LEVEL)
        parser.add_argument("-s", "--service", action="store_true", default=False, help="Running as a service and should log to file")

        parser.add_argument("-f", "--file", action="store", type=str, default=None, help="Config file")
        parser.add_argument("-c", "--config", action="store", type=str, default=None, help="Config as JSON string")

        params = parser.parse_args()

        setup(path_log=params.path_log, loglevel=params.loglevel, service=params.service)

        if params.file and params.config:
            config_edit(params.file, params.config)


    except KeyboardInterrupt:
        print("Terminated by CTRL-C")
        exit()


##############################################################################################################
# Init


if __name__ == "__main__":
    main()