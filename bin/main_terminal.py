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

#### Config ####
import configparser

#### Variables ####
from collections import defaultdict

#### JSON ####
import json

#### Encryption ####
import crypt
from hmac import compare_digest as compare_hash

#### Terminal ####
import subprocess
import pty
import termios
import select
import struct
import fcntl
import shlex
import signal

#### Webserver ####
# Install: pip3 install flask
# Source: 
from flask import Flask, send_from_directory, redirect

#### Webserver Basic Auth ####
# Install: pip3 install flask_httpauth
# Source: 
from flask_httpauth import HTTPBasicAuth

#### Webserver Socket ####
# Install: pip3 install flask_socketio
# Source: 
from flask_socketio import SocketIO


##############################################################################################################
# Globals


#### Global Variables - Configuration ####
NAME = "Terminal"
DESCRIPTION = "Simple and easy web terminal"
VERSION = "0.0.1 (2022-10-21)"
COPYRIGHT = "(c) 2022 Sebastian Obele  /  obele.eu"
#PATH = os.path.expanduser("~") + "/." + os.path.splitext(os.path.basename(__file__))[0]
#PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.dirname(os.path.abspath(__file__)).rstrip("/bin")




#### Global Variables - System (Not changeable) ####
CONFIG = None
CONFIG_AUTH = None

app = Flask(__name__)
app.config["fd"] = None
app.config["pid"] = None
socketio = SocketIO(app)
auth_handler = HTTPBasicAuth()


##############################################################################################################
# Terminal


def terminal_setup():
    if app.config["pid"]:
        return

    (pid, fd) = pty.fork()
    if pid == 0:
        if app.config["path"] != "": os.chdir(app.config["path"])
        subprocess.run(app.config["cmd"])
    else:
        app.config["fd"] = fd
        app.config["pid"] = pid
        terminal_size(fd, 50, 50)
        socketio.start_background_task(target=terminal_output)




def terminal_size(fd, rows, cols, xpix=0, ypix=0):
    if fd:
        size = struct.pack("HHHH", rows, cols, xpix, ypix)
        fcntl.ioctl(fd, termios.TIOCSWINSZ, size)




def terminal_input(fd, data):
    if fd:
        os.write(fd, data.encode())




def terminal_output():
    max_read_bytes = 1024 * 20
    while True:
        socketio.sleep(0.01)
        if app.config["fd"]:
            timeout_sec = 0
            (data_ready, _, _) = select.select([app.config["fd"]], [], [], timeout_sec)
            if data_ready:
                output = ""
                try:
                    output = os.read(app.config["fd"], max_read_bytes).decode()
                except Exception as e:
                    output = str(e)
                    if e.errno == 5:
                        pid = app.config["pid"]
                        app.config["fd"] = None
                        app.config["pid"] = None
                        socketio.emit("json", {"version": VERSION, "result": "1", "cmd": "exit"}, namespace="/terminal")
                        os.kill(pid, signal.SIGTERM)
                        break

                socketio.emit("json", {"version": VERSION, "result": "1", "data": output}, namespace="/terminal")


##############################################################################################################
# Webserver


@auth_handler.verify_password
def handle_auth(username, password):
    if app.config["auth"]:
        if username != "" and password != "":
            if CONFIG_AUTH.has_section("user"):
                if CONFIG_AUTH.has_option("user", "any") or CONFIG_AUTH.has_option("user", "all") or CONFIG_AUTH.has_option("user", "anybody"):
                    return username
                for (key, val) in CONFIG_AUTH.items("user"):
                    if key != "" and val != "":
                        if username == key and compare_hash(crypt.crypt(password, val), val):
                            return username
    else:
        return username
    return False




@app.route("/<path:filename>")
@auth_handler.login_required
def handle_files(filename):
    return send_from_directory(app.config["path_root"], filename)




@auth_handler.login_required
def handle_root():
    return send_from_directory(app.config["path_root"], app.config["path_redirect_root"])




def handle_not_found(data):
    return redirect(app.config["path_redirect_not_found"], code=302)




@socketio.on("connect", namespace="/terminal")
@auth_handler.login_required
def webserver_connect():
    terminal_setup()
    socketio.emit("json", {"version": VERSION, "result": "1"}, namespace="/terminal")




@socketio.on("json", namespace="/terminal")
@auth_handler.login_required
def webserver_input(data):
    if data["cmd"] == "get_config":
        config_interface = defaultdict(dict)

        lng_key = ""
        lng_delimiter = ""

        if CONFIG.has_section("main"):
            if CONFIG.has_option("main", "lng_auto") and CONFIG.has_option("main", "lng"):
                if "lng" not in data or not CONFIG["main"].getboolean("lng_auto"):
                    data["lng"] = CONFIG["main"]["lng"]
                lng_key, lng_delimiter = build_lng(data["lng"])
    
        if CONFIG.has_section("interface_terminal_main"):
            mapping_main = "main"
            if CONFIG.has_option("interface_mapping", "main"):
                mapping_main = CONFIG["interface_mapping"]["main"]
            for (key, val) in CONFIG.items("interface_terminal_main"):
                if val != "":
                    if lng_delimiter != "" and lng_delimiter in key:
                        if lng_key in key:
                            key = key.replace(lng_key, "")
                            if CONFIG.has_option("interface_mapping", key):
                                config_interface[mapping_main][CONFIG["interface_mapping"][key]] = val
                            else:
                                config_interface[mapping_main][key] = val
                    else:
                        if CONFIG.has_option("interface_mapping", key):
                            config_interface[mapping_main][CONFIG["interface_mapping"][key]] = val
                        else:
                            config_interface[mapping_main][key] = val

        socketio.emit("json", {"version": VERSION, "result": "1", "config": config_interface}, namespace="/terminal")

    if data["cmd"] == "input":
        terminal_input(app.config["fd"], data["data"])

    if data["cmd"] == "resize":
        terminal_size(app.config["fd"], data["data"]["rows"], data["data"]["cols"])


##############################################################################################################
# Build


def build_lng(lng):
    if CONFIG.has_option("interface_process", "lng") and CONFIG.has_option("interface_process", "lng_delimiter"):
        lng_delimiter = CONFIG["interface_process"]["lng_delimiter"]
        lng = lng.replace(lng_delimiter, "")
        if CONFIG["interface_process"].getboolean("lng") and CONFIG["interface_process"]["lng_delimiter"] != "" and lng != "":
            lng_key = CONFIG["interface_process"]["lng_delimiter"] + lng;
        else:
            lng_key = "";
    else:
        lng_delimiter = "";
        lng_key = "";
    return [lng_key, lng_delimiter]


##############################################################################################################
# User


def user_get(file):
    global CONFIG_AUTH
    if not CONFIG_AUTH:
        if not config_auth_read(file):
            panic()

    if not CONFIG_AUTH.has_section("user"): CONFIG_AUTH.add_section("user")
    for (key, val) in CONFIG_AUTH.items("user"):
        print(key)
    exit()




def user_delete(file, user):
    global CONFIG_AUTH
    if not CONFIG_AUTH:
        if not config_auth_read(file):
            panic()

    if not CONFIG_AUTH.has_section("user"): CONFIG_AUTH.add_section("user")

    if CONFIG_AUTH.has_option("user", user):
        CONFIG_AUTH.remove_option("user", user)
        text = "OK: User '" + user + "' deleted!"
    else:
        text = "Error: User '" + user + "' not found!"

    if not config_auth_save(file):
        text = "Error"

    print(text)
    exit()




def user_set(file, user, password):
    global CONFIG_AUTH
    if not CONFIG_AUTH:
        if not config_auth_read(file):
            panic()
    
    if not CONFIG_AUTH.has_section("user"): CONFIG_AUTH.add_section("user")

    if CONFIG_AUTH.has_option("user", user):
        text = "OK: User '" + user + "' changed!"
    else:
        text = "OK: User '" + user + "' added!"

    CONFIG_AUTH["user"][user] = crypt.crypt(password)

    if not config_auth_save(file):
        text = "Error"

    print(text)
    exit()


##############################################################################################################
# Config


#### Config - Get #####
def config_get(config, section, key, default="", lng_key=""):
    if not config or section == "" or key == "": return default
    if not config.has_section(section): return default
    if config.has_option(section, key+lng_key):
        return config[section][key+lng_key]
    elif config.has_option(section, key):
        return config[section][key]
    return default


def config_getint(config, section, key, default=0, lng_key=""):
    if not config or section == "" or key == "": return default
    if not config.has_section(section): return default
    if config.has_option(section, key+lng_key):
        return config.getint(section, key+lng_key)
    elif config.has_option(section, key):
        return config.getint(section, key)
    return default


def config_getboolean(config, section, key, default=False, lng_key=""):
    if not config or section == "" or key == "": return default
    if not config.has_section(section): return default
    if config.has_option(section, key+lng_key):
        return config[section].getboolean(key+lng_key)
    elif config.has_option(section, key):
        return config[section].getboolean(key)
    return default


def config_getsection(config, section, default="", lng_key=""):
    if not config or section == "": return default
    if not config.has_section(section): return default
    if config.has_section(section+lng_key):
        return key+lng_key
    elif config.has_section(section):
        return key
    return default


def config_getoption(config, section, key, default=False, lng_key=""):
    if not config or section == "" or key == "": return default
    if not config.has_section(section): return default
    if config.has_option(section, key+lng_key):
        return key+lng_key
    elif config.has_option(section, key):
        return key
    return default




#### Config - Read #####
def config_read(file=None):
    global CONFIG

    if file is None:
        return False
    else:
        CONFIG = configparser.ConfigParser(allow_no_value=True, inline_comment_prefixes="#")
        CONFIG.sections()
        if os.path.isfile(file):
            try:
                CONFIG.read(file, encoding='utf-8')
            except Exception as e:
                return False
        else:
            if not config_default(file=file):
                return False
    return True




#### Config - Save #####
def config_save(file=None):
    global CONFIG

    if file is None:
        return False
    else:
        if os.path.isfile(file):
            try:
                with open(file,"w") as file:
                    CONFIG.write(file)
            except Exception as e:
                return False
        else:
            return False
    return True




#### Config - Default #####
def config_default(file=None):
    global CONFIG

    if file is None:
        return False
    elif DEFAULT_CONFIG != "":
        if not os.path.isdir(os.path.dirname(file)):
            try:
                os.makedirs(os.path.dirname(file))
            except Exception:
                return False
        try:
            config_file = open(file, "w")
            config_file.write(DEFAULT_CONFIG)
            config_file.close()
            if not config_read(file=file):
                return False
        except:
            return False
    else:
        return False

    if not CONFIG.has_section("main"): CONFIG.add_section("main")
    CONFIG["main"]["default_config"] = "True"
    return True


##############################################################################################################
# Config Auth


#### Config Auth - Read #####
def config_auth_read(file=None):
    global CONFIG_AUTH

    if file is None:
        return False
    else:
        CONFIG_AUTH = configparser.ConfigParser(allow_no_value=True, inline_comment_prefixes="#")
        CONFIG_AUTH.sections()
        if os.path.isfile(file):
            try:
                CONFIG_AUTH.read(file, encoding='utf-8')
            except Exception as e:
                return False
        else:
            if not config_auth_default(file=file):
                return False
    return True




#### Config Auth - Save #####
def config_auth_save(file=None):
    global CONFIG_AUTH

    if file is None:
        return False
    else:
        if os.path.isfile(file):
            try:
                with open(file,"w") as file:
                    CONFIG_AUTH.write(file)
            except Exception as e:
                return False
            config_auth_external()
        else:
            return False
    return True




#### Config Auth - Default #####
def config_auth_default(file=None):
    global CONFIG_AUTH

    if file is None:
        return False
    elif DEFAULT_CONFIG_AUTH != "":
        if not os.path.isdir(os.path.dirname(file)):
            try:
                os.makedirs(os.path.dirname(file))
            except Exception:
                return False
        try:
            config_file = open(file, "w")
            config_file.write(DEFAULT_CONFIG_AUTH)
            config_file.close()
            if not config_auth_read(file=file):
                return False
            config_auth_external()
        except:
            return False
    else:
        return False

    if not CONFIG_AUTH.has_section("main"): CONFIG_AUTH.add_section("main")
    CONFIG_AUTH["main"]["default_config"] = "True"
    return True




#### Config Auth - External #####
def config_auth_external():
    if CONFIG is not None:
        if CONFIG.has_option("path", "auth_external"):
            if CONFIG["path"]["auth_external"] != "":
                try:
                    data = ""
                    for (key, val) in CONFIG_AUTH.items("user"):
                        if key != "" and val != "":
                            data = data + key + ":" + val + "\n"
                    file = open(CONFIG["path"]["auth_external"], "w")
                    file.write(data)
                    file.close()
                except:
                    return False
        return True


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
def setup(path=None, path_log=None, loglevel=None, service=False, auth=None, auth_file=""):
    global PATH
    global LOG_LEVEL
    global LOG_FILE

    if path is not None:
        PATH = path

    if loglevel is not None:
        LOG_LEVEL = loglevel

    if service:
        LOG_LEVEL = LOG_LEVEL_SERVICE
        if path_log is not None:
            LOG_FILE = path_log
        else:
            LOG_FILE = PATH
        LOG_FILE = LOG_FILE + "/" + NAME + ".log"

    config_read(PATH + "/config.cfg")

    if auth and auth_file != "":
        if not auth_file.startswith("/"):
            auth_file = PATH + "/" + auth_file
        if not config_auth_read(auth_file):
            panic()

    app.config["auth"] = auth




#### Setup #####
def setup_log():
    log("...............................................................................", LOG_INFO)
    log("        Name: " + NAME, LOG_INFO)
    log("              " + DESCRIPTION, LOG_INFO)
    log("Program File: " + __file__, LOG_INFO)
    log("     Version: " + VERSION, LOG_INFO)
    log("   Copyright: " + COPYRIGHT, LOG_INFO)
    log("...............................................................................", LOG_INFO)




#### Setup #####
def setup_connection(host, port, path_root, path_redirect_root, path_redirect_not_found, path_terminal, cmd, cmd_args):
    app.config["path_root"] = path_root
    app.config["path_redirect_root"] = path_redirect_root
    app.config["path_redirect_not_found"] = path_redirect_not_found
    app.config["path"] = path_terminal
    app.config["cmd"] = [cmd] + shlex.split(cmd_args)
    if path_redirect_not_found != "": app.register_error_handler(404, handle_not_found)
    if path_redirect_root != "": app.add_url_rule('/', 'root', handle_root)
    socketio.run(app, host=host, port=port)




#### Start ####
def main():
    try:
        description = NAME + " - " + DESCRIPTION
        parser = argparse.ArgumentParser(description=description)

        parser.add_argument("--host", action="store", type=str, default="127.0.0.1", help="Host to run server (Use 0.0.0.0 to allow access from anywhere)")
        parser.add_argument("--port", action="store", type=int, default=8181, help="Port to run server")
        parser.add_argument("--path_root", action="store", type=str, default="www", help="Server root path")
        parser.add_argument("--path_redirect_root", action="store", type=str, default="terminal.html", help="Root/Index file")
        parser.add_argument("--path_redirect_not_found", action="store", type=str, default="terminal.html", help="Redirect file")
        parser.add_argument("--auth", action="store_true", default=True, help="Enable authentication")
        parser.add_argument("--auth_file", action="store", type=str, default="config_auth.cfg", help="Authentication/User config file")
        parser.add_argument("--path_terminal", action="store", type=str, default="/tmp", help="Terminal start path")
        parser.add_argument("--cmd", action="store", type=str, default="bash", help="Command to run in the terminal")
        parser.add_argument("--cmd_args", action="store", type=str, default="", help="Arguments to pass to command (i.e. --args='arg1 arg2 --flag')",)

        parser.add_argument("-p", "--path", action="store", type=str, default=None, help="Path to alternative config directory")
        parser.add_argument("-pl", "--path_log", action="store", type=str, default=None, help="Path to alternative log directory")
        parser.add_argument("-l", "--loglevel", action="store", type=int, default=LOG_LEVEL)
        parser.add_argument("-s", "--service", action="store_true", default=False, help="Running as a service and should log to file")

        parser.add_argument("--userget", action="store_true", default=False, help="User administration - List all users")
        parser.add_argument("--userdelete", action="store", type=str, default=None, help="User administration - Delete USER")
        parser.add_argument("--user", action="store", type=str, default=None, help="User administration - Edit/Add USER")
        parser.add_argument("--password", action="store", type=str, default=None, help="User administration - Set PASSWORD")

        params = parser.parse_args()

        setup(path=params.path, path_log=params.path_log, loglevel=params.loglevel, service=params.service, auth=params.auth, auth_file=params.auth_file)

        if not params.auth_file.startswith("/"):
            params.auth_file = PATH + "/" + params.auth_file

        if params.userget:
            user_get(params.auth_file)

        if params.userdelete:
            user_delete(params.auth_file, params.userdelete)

        if params.user and params.password:
            user_set(params.auth_file, params.user, params.password)

        setup_log()
        setup_connection(host=params.host, port=params.port, path_root=params.path_root, path_redirect_root=params.path_redirect_root, path_redirect_not_found=params.path_redirect_not_found, path_terminal=params.path_terminal, cmd=params.cmd, cmd_args=params.cmd_args)

    except KeyboardInterrupt:
        print("Terminated by CTRL-C")
        exit()


##############################################################################################################
# Files


#### Default configuration file ####
DEFAULT_CONFIG = ''''''




DEFAULT_CONFIG_AUTH = '''
[user]
#any
admin=$6$O2nSzkoi1MAfzlPc$/FxL6L//8/OV0hvnP8.xrEpavwgzqzlnAfN82goExuWFeAUJLpZS/LzJ1gI5hCioBg4reI/aSm/18.o59omA.0
'''


##############################################################################################################
# Init


if __name__ == "__main__":
    main()