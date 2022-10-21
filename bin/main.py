#!/usr/bin/env python3
#test
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
from vendor.configobj import ConfigObj
import configparser

#### Variables ####
from collections import defaultdict
import copy

#### Files ####
from pathlib import Path
import shutil
import glob
import tarfile

#### JSON ####
import json
import pickle

#### String ####
import string

#### Regex ####
import re

#### Encryption ####
import crypt
from hmac import compare_digest as compare_hash

#### Process ####
import signal
import threading

#### External process ####
import subprocess
import socket

#### System Sensors ####
# Install: pip3 install psutil
import psutil

#### Software ####
import pkg_resources

#### Internal ####
from convert import convert_class
from terminal import terminal_class
from variables_system import variables_system_class
from variables_user import variables_user_class


##############################################################################################################
# Globals


#### Global Variables - Configuration ####
NAME = "ConfigInterfaceTool"
DESCRIPTION = "Easy, minimalistic and simple interface for device/application administration and configuration."
VERSION = "0.0.1 (2022-10-21)"
COPYRIGHT = "(c) 2022 Sebastian Obele  /  obele.eu"
#PATH = os.path.expanduser("~") + "/." + os.path.splitext(os.path.basename(__file__))[0]
#PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.dirname(os.path.abspath(__file__)).rstrip("/bin")




#### Global Variables - System (Not changeable) ####
CONFIG = None
CONFIG_AUTH = None

CONFIG_FILES = None
CONFIG_VARIABLES = None
CONFIG_VARIABLES_INTERFACE = None
CONFIG_INTERFACE = None
CONFIG_SOFTWARE = None
CONFIG_WIZARD = None

VARIABLES = None
VARIABLES_SESSION = None
VARIABLES_SYSTEM = None
VARIABLES_USER = None
VARIABLES_DATA = None
VARIABLES_SOFTWARE = None


TERMINAL = None


##############################################################################################################
# Process AUTH


def process_auth(username, password):
    if username != "" and password != "":
        if CONFIG_AUTH.has_section("user"):
            if CONFIG_AUTH.has_option("user", "any") or CONFIG_AUTH.has_option("user", "all") or CONFIG_AUTH.has_option("user", "anybody"):
                return True
            for (key, val) in CONFIG_AUTH.items("user"):
                if key != "" and val != "":
                    if username == key and compare_hash(crypt.crypt(password, val), val):
                        return True
        return False;


##############################################################################################################
# Process GET


def process_get(receive):
    log("Process GET - Receive: " + receive, LOG_DEBUG)

    send_json = defaultdict(dict)
    send_json["version"] = VERSION
    send_json["result"] = "0"

    if receive != "":
        receive_json = json.loads(receive)

        if("uid" in receive_json and "cmd" in receive_json):
            send_json["uid"] = receive_json["uid"]
            error = []

            if "lng" not in receive_json or not CONFIG["main"].getboolean("lng_auto"):
                receive_json["lng"] = CONFIG["main"]["lng"]
            lng_key, lng_delimiter = build_lng(receive_json["lng"])

            if "cmd_mode" not in receive_json:
                receive_json["cmd_mode"] = ""
            elif receive_json["cmd_mode"] != "":
                receive_json["cmd_mode"] = "_" + receive_json["cmd_mode"]

            if receive_json["cmd"] == "get_config" or receive_json["cmd"] == "get_config_data":
                if CONFIG["config_process"].getboolean("variables_system"):
                    if not VARIABLES_SYSTEM.config_get(): error.append("variables_system - config_get")
                    log("VARIABLES_SYSTEM", LOG_DEBUG)
                    log(VARIABLES_SYSTEM.data, LOG_DEBUG)
                if CONFIG["config_process"].getboolean("variables_user"):
                    if not VARIABLES_USER.config_get(): error.append("variables_user - config_get")
                    log("VARIABLES_USER", LOG_DEBUG)
                    log(VARIABLES_USER.data, LOG_DEBUG)
                error = error + build("config" + receive_json["cmd_mode"], receive_json["lng"])
                send_json["config"] = json.loads(CONFIG_INTERFACE)

            if receive_json["cmd"] == "get_data" or receive_json["cmd"] == "get_config_data":
                if CONFIG["config_process"].getboolean("variables_system"):
                    if not VARIABLES_SYSTEM.data_get(receive_json, send_json): error.append("variables_system - data_get")
                if CONFIG["config_process"].getboolean("variables_user"):
                    if not VARIABLES_USER.data_get(receive_json, send_json): error.append("variables_user - data_get")
                error = error + build("data" + receive_json["cmd_mode"], receive_json["lng"])
                if CONFIG["main"].getboolean("mode_data"):
                    for key in VARIABLES:
                        send_json["data"][key] = VARIABLES[key]
                elif "data" in receive_json:
                    if isinstance(receive_json["data"], list):
                        for key in receive_json["data"]:
                            if key in VARIABLES:
                                send_json["data"][key] = VARIABLES[key]
                            else:
                                send_json["data"][key] = ""
                                if isinstance(CONFIG_VARIABLES[key]["data_get_cmd"], str):
                                    if CONFIG_VARIABLES[key]["data_get_cmd"] != "":
                                        try:
                                            result = subprocess.run(CONFIG_VARIABLES[key]["data_get_cmd"], capture_output=True, shell=True, text=True, timeout=5)
                                            if result.returncode == 0:
                                                send_json["data"][key] = send_json["data"][key] + re.sub(r'^\s+|\s+$', '', result.stdout) + "\n\n"
                                        except:
                                            None
                                if isinstance(CONFIG_VARIABLES[key]["data_get_file"], str):
                                    if CONFIG_VARIABLES[key]["data_get_file"] != "":
                                        try:
                                            file_handler = open(CONFIG_VARIABLES[key]["data_get_file"])
                                            send_json["data"][key] = send_json["data"][key] + file_handler.read() + "\n\n"
                                            file_handler.close()
                                        except:
                                            None
                else:
                    for key in CONFIG_VARIABLES_INTERFACE:
                        if key in VARIABLES:
                            send_json["data"][key] = VARIABLES[key]

                if CONFIG["config"].getboolean("enabled"):
                    if not process_config_get(receive_json, send_json): error.append("process_config_get")

            if receive_json["cmd"] == "get_live_config" or receive_json["cmd"] == "get_live_config_data":
                if CONFIG["software"].getboolean("enabled"):
                    if not process_software_get(receive_json, send_json): error.append("process_software_get")
                if CONFIG["wizard"].getboolean("enabled"):
                    if not process_wizard_get(receive_json, send_json): error.append("process_wizard_get")

            if len(error) > 0:
                log("Process GET: " + ", ".join(error), LOG_ERROR)
                send_json["result"] = "0"
                send_json["msg"] = "\n".join(error)
            else:
                send_json["result"] = "1"

    for key in VARIABLES_SESSION:
        send_json["session"][key] = VARIABLES_SESSION[key]

    send = json.dumps(send_json)
    log("Process GET - Send: " + send, LOG_DEBUG)
    return send


##############################################################################################################
# Process POST


def process_post(receive):
    log("Process POST - Receive: " + receive, LOG_DEBUG)

    send_json = defaultdict(dict)
    send_json["version"] = VERSION
    send_json["result"] = "0"

    if receive != "":
        receive_json = json.loads(receive)

        if "lng" not in receive_json or not CONFIG["main"].getboolean("lng_auto"):
            receive_json["lng"] = CONFIG["main"]["lng"]
        lng_key, lng_delimiter = build_lng(receive_json["lng"])

        if "cmd_mode" not in receive_json:
            receive_json["cmd_mode"] = ""
        elif receive_json["cmd_mode"] != "":
            receive_json["cmd_mode"] = "_" + receive_json["cmd_mode"]

        if "uid" in receive_json and "cmd" in receive_json and "data" in receive_json:
            send_json["uid"] = receive_json["uid"]
            error = []
            state_execute = False
            state_cmd = False
            state_script = False

            if CONFIG["config_process"].getboolean("variables_system"):
                if not VARIABLES_SYSTEM.data_set(receive_json, send_json): error.append("variables_system - data_set")
            if CONFIG["config_process"].getboolean("variables_user"):
                if not VARIABLES_USER.data_set(receive_json, send_json): error.append("variables_user - data_set")
            if CONFIG["config"].getboolean("enabled"):
                if not process_config_set(receive_json, send_json): error.append("process_config_set")
            if CONFIG["software"].getboolean("enabled"):
                if not process_software_set(receive_json, send_json): error.append("process_software_set")
            if CONFIG["wizard"].getboolean("enabled"):
                if not process_wizard_set(receive_json, send_json): error.append("process_wizard_set")

            for key in receive_json["data"].keys():
                if key in VARIABLES_DATA:
                    if process_value_regex_match(key, receive_json["data"][key]):
                        log("Update Variable: " + key + " -> " + receive_json["data"][key], LOG_EXTREME)
                        VARIABLES_DATA[key] = receive_json["data"][key]
                        if CONFIG["config_process"].getboolean("require_acknowledge"):
                            if isinstance(CONFIG_VARIABLES[key]["require_acknowledge"], str):
                                if val_to_bool(CONFIG_VARIABLES[key]["require_acknowledge"]): VARIABLES_SESSION["require_acknowledge"] = True
                        if CONFIG["config_process"].getboolean("require_reboot"):
                            if isinstance(CONFIG_VARIABLES[key]["require_reboot"], str):
                                if val_to_bool(CONFIG_VARIABLES[key]["require_reboot"]): VARIABLES_SESSION["require_reboot"] = True
                        if CONFIG["config_process"].getboolean("require_reload"):
                            if isinstance(CONFIG_VARIABLES[key]["require_reload"], str):
                                if val_to_bool(CONFIG_VARIABLES[key]["require_reload"]): VARIABLES_SESSION["require_reload"] = True
                    else:
                        log("Not update Variable (Regex not matched): " + key + " -> " + receive_json["data"][key], LOG_EXTREME)
                elif CONFIG.has_option("config_process", "variables_session_prefix"):
                    if key.startswith(CONFIG["config_process"]["variables_session_prefix"]):
                        key_session = key.replace(CONFIG["config_process"]["variables_session_prefix"], "")
                        if key_session in VARIABLES_SESSION:
                            log("Update Session Variable: " + key_session + " -> " + receive_json["data"][key], LOG_EXTREME)
                            VARIABLES_SESSION[key_session] = receive_json["data"][key]

            if CONFIG["config_process"].getboolean("execute"):
                for page in CONFIG_FILES.keys():
                    if isinstance(CONFIG_FILES[page]["main"]["execute"], str):
                        if execute(CONFIG_FILES[page]["main"]["execute"], receive_json["data"]):
                            state_execute = True

            if state_execute == True:
                log("**** Execute ****", LOG_DEBUG)
                if not data_save(): error.append("data_save")

                if CONFIG["config"].getboolean("backup_auto"):
                    file = CONFIG["path"]["backup"] + "/" + time.strftime(re.sub(r'([a-zA-Z])', r'%\1', CONFIG["config"]["backup_auto_time_format"]), time.localtime(time.time())) + CONFIG["config"]["backup_auto_name"] + "." + CONFIG["config"]["extension"]
                    file_source = CONFIG["path"]["config"] + "/config_current." + CONFIG["config"]["extension"]
                    shutil.copyfile(file_source, file)
                    backup_auto_max = CONFIG.getint("config", "backup_auto_max")
                    if backup_auto_max > 0:
                        files = glob.glob(CONFIG["path"]["backup"] + "/*" + CONFIG["config"]["backup_auto_name"] + "." + CONFIG["config"]["extension"], recursive=False)
                        if len(files) > backup_auto_max:
                            files.sort(key=os.path.getmtime, reverse=True)
                            i = 0
                            for file in files:
                                i += 1
                                if i > backup_auto_max:
                                    os.remove(file)

                    if CONFIG["config"].getboolean("backup_auto_files"):
                        with tarfile.open(file + "." + CONFIG["config"]["extension_archive"], "w") as archive:
                            for page in CONFIG_FILES.keys():
                                if isinstance(CONFIG_FILES[page]["main"]["execute"], str):
                                    if execute(CONFIG_FILES[page]["main"]["execute"], receive_json["data"]):
                                        for key in CONFIG_FILES[page]["files"].keys():
                                            if isinstance(CONFIG_FILES[page]["files_type"][key], str):
                                                if CONFIG_FILES[page]["files_type"][key] in CONFIG["config"]["backup_auto_files_exclude_type"]:
                                                    continue
                                            if CONFIG["main"].getboolean("mode_test"):
                                                file = CONFIG["path"]["mode_test"] + CONFIG_FILES[page]["files"][key]
                                            else:
                                                file = CONFIG_FILES[page]["files"][key]
                                            if os.path.isfile(file):
                                                archive.add(file)

                state_restore_files = False
                if CONFIG["config"].getboolean("backup_auto") and CONFIG["config"].getboolean("backup_auto_files_restore") and "app_config_auto_restore" in receive_json["data"]: state_restore_files = True
                if CONFIG["config"].getboolean("backup_user") and CONFIG["config"].getboolean("backup_user_files_restore") and "app_config_user_restore" in receive_json["data"]: state_restore_files = True
                if CONFIG["config"].getboolean("backup_factory") and CONFIG["config"].getboolean("backup_factory_files_restore") and "app_config_factory_restore" in receive_json["data"]: state_restore_files = True
                if state_restore_files:
                    if os.path.isfile(receive_json["data"]["app_config_files"] + "." + CONFIG["config"]["extension_archive"]):
                        archive = tarfile.open(receive_json["data"]["app_config_files"] + "." + CONFIG["config"]["extension_archive"], "r")
                    else:
                        archive = None
                        error.append("archive_file - " + receive_json["data"]["app_config_files"] + "." + CONFIG["config"]["extension_archive"])

                process_variable_merge()
                process_value_replace()
                process_value_regex()
                process_value_convert()

                log("Execute - Searching cmd_before...", LOG_DEBUG)
                for page in CONFIG_FILES.keys():
                    if isinstance(CONFIG_FILES[page]["main"]["execute"], str):
                        if execute(CONFIG_FILES[page]["main"]["execute"], receive_json["data"]):
                            log("Found excute in config file: " + page, LOG_DEBUG)

                            error_ignore = False
                            if CONFIG["config_process"].getboolean("error_ignore"):
                                if isinstance(CONFIG_FILES[page]["main"]["error_ignore"], str):
                                    error_ignore = val_to_bool(CONFIG_FILES[page]["main"]["error_ignore"])

                            if CONFIG["config_process"].getboolean("cmd"):
                                if isinstance(CONFIG_FILES[page]["main"]["cmd_before"], str):
                                    if not execute_cmd(CONFIG_FILES[page]["main"]["cmd_before"]) and not error_ignore: error.append(page + " - cmd_before: " + CONFIG_FILES[page]["main"]["cmd_before"])

                            if CONFIG["config_process"].getboolean("script"):
                                if isinstance(CONFIG_FILES[page]["main"]["script_before"], str):
                                    if not execute_script(CONFIG_FILES[page]["main"]["script_before"]) and not error_ignore: error.append(page + " - script_before: " + CONFIG_FILES[page]["main"]["script_before"])

                log("Execute - Searching file...", LOG_DEBUG)
                for page in CONFIG_FILES.keys():
                    if isinstance(CONFIG_FILES[page]["main"]["execute"], str):
                        if execute(CONFIG_FILES[page]["main"]["execute"], receive_json["data"]):
                            log("Found excute in config file: " + page, LOG_DEBUG)

                            error_ignore = False
                            if CONFIG["config_process"].getboolean("error_ignore"):
                                if isinstance(CONFIG_FILES[page]["main"]["error_ignore"], str):
                                    error_ignore = val_to_bool(CONFIG_FILES[page]["main"]["error_ignore"])

                            if CONFIG["config_process"].getboolean("require_acknowledge"):
                                if isinstance(CONFIG_FILES[page]["main"]["require_acknowledge"], str):
                                     if val_to_bool(CONFIG_FILES[page]["main"]["require_acknowledge"]): VARIABLES_SESSION["require_acknowledge"] = True

                            if CONFIG["config_process"].getboolean("require_reboot"):
                                if isinstance(CONFIG_FILES[page]["main"]["require_reboot"], str):
                                    if val_to_bool(CONFIG_FILES[page]["main"]["require_reboot"]): VARIABLES_SESSION["require_reboot"] = True

                            if CONFIG["config_process"].getboolean("require_reload"):
                                if isinstance(CONFIG_FILES[page]["main"]["require_reload"], str):
                                    if val_to_bool(CONFIG_FILES[page]["main"]["require_reload"]): VARIABLES_SESSION["require_reload"] = True

                            if CONFIG["config_process"].getboolean("files"):
                                for key in CONFIG_FILES[page]["files"].keys():
                                    if isinstance(CONFIG_FILES[page]["files_type"][key], str):
                                        type = CONFIG_FILES[page]["files_type"][key]
                                    else:
                                        type = "text"

                                    if isinstance(CONFIG_FILES[page]["files_permission"][key], str):
                                        permission = CONFIG_FILES[page]["files_permission"][key]
                                    else:
                                        permission = None

                                    if isinstance(CONFIG_FILES[page]["files_owner"][key], str):
                                        owner = CONFIG_FILES[page]["files_owner"][key]
                                    else:
                                        owner = None

                                    if state_restore_files:
                                        if archive:
                                            if CONFIG["main"].getboolean("mode_test"):
                                                file = CONFIG["path"]["mode_test"] + CONFIG_FILES[page]["files"][key]
                                            else:
                                                file = CONFIG_FILES[page]["files"][key]
                                            try:
                                                archive.extract(file.lstrip("/"), "/")
                                            except KeyError:
                                                None
                                    else:
                                        if not execute_file(CONFIG["path"]["config_templates"] + "/" + key, CONFIG_FILES[page]["files"][key], key, type, permission, owner) and not error_ignore: error.append(page + " - file: " + key + " -> " + CONFIG_FILES[page]["files"][key])

                log("Execute - Searching cmd_after...", LOG_DEBUG)
                for page in CONFIG_FILES.keys():
                    if isinstance(CONFIG_FILES[page]["main"]["execute"], str):
                        if execute(CONFIG_FILES[page]["main"]["execute"], receive_json["data"]):
                            log("Found excute in config file: " + page, LOG_DEBUG)

                            error_ignore = False
                            if CONFIG["config_process"].getboolean("error_ignore"):
                                if isinstance(CONFIG_FILES[page]["main"]["error_ignore"], str):
                                    error_ignore = val_to_bool(CONFIG_FILES[page]["main"]["error_ignore"])

                            if CONFIG["config_process"].getboolean("cmd"):
                                if isinstance(CONFIG_FILES[page]["main"]["cmd_after"], str):
                                    if not execute_cmd(CONFIG_FILES[page]["main"]["cmd_after"]) and not error_ignore: error.append(page + " - cmd_after: " + CONFIG_FILES[page]["main"]["cmd_after"])

                                if isinstance(CONFIG_FILES[page]["main"]["cmd"], str):
                                    if not execute_cmd(CONFIG_FILES[page]["main"]["cmd"]) and not error_ignore: error.append(page + " - cmd: " + CONFIG_FILES[page]["main"]["cmd"])

                            if CONFIG["config_process"].getboolean("script"):
                                if isinstance(CONFIG_FILES[page]["main"]["script_after"], str):
                                    if not execute_script(CONFIG_FILES[page]["main"]["script_after"]) and not error_ignore: error.append(page + " - script_after: " + CONFIG_FILES[page]["main"]["script_after"])

                                if isinstance(CONFIG_FILES[page]["main"]["script"], str):
                                    if not execute_script(CONFIG_FILES[page]["main"]["script"]) and not error_ignore: error.append(page + " - script: " + CONFIG_FILES[page]["main"]["script"])

                if state_restore_files:
                    if archive:
                        archive.close()

            for key in receive_json["data"].keys():
                error_ignore = False
                if CONFIG["config_process"].getboolean("error_ignore"):
                    if isinstance(CONFIG_VARIABLES[key]["error_ignore"], str):
                        error_ignore = val_to_bool(CONFIG_VARIABLES[key]["error_ignore"])

                if CONFIG["config_process"].getboolean("value_cmd"):
                    if isinstance(CONFIG_VARIABLES[key]["value_cmd"], str):
                        if CONFIG_VARIABLES[key]["value_cmd"] != "":
                            state_cmd = True
                            if not execute_cmd(process_variable_cmd(CONFIG_VARIABLES[key]["value_cmd"], "value", VARIABLES_DATA[key])) and not error_ignore: error.append(key + " - value_cmd: " + CONFIG_VARIABLES[key]["value_cmd"])
                    if isinstance(CONFIG_VARIABLES[key]["value_cmd_true"], str):
                        if CONFIG_VARIABLES[key]["value_cmd_true"] != "" and val_to_bool(receive_json["data"][key]):
                            state_cmd = True
                            if not execute_cmd(process_variable_cmd(CONFIG_VARIABLES[key]["value_cmd_true"], "value", VARIABLES_DATA[key])) and not error_ignore: error.append(key + " - value_cmd_true: " + CONFIG_VARIABLES[key]["value_cmd_true"])
                    if isinstance(CONFIG_VARIABLES[key]["value_cmd_false"], str):
                        if CONFIG_VARIABLES[key]["value_cmd_false"] != "" and not val_to_bool(receive_json["data"][key]):
                            state_cmd = True
                            if not execute_cmd(process_variable_cmd(CONFIG_VARIABLES[key]["value_cmd_false"], "value", VARIABLES_DATA[key])) and not error_ignore: error.append(key + " - value_cmd_false: " + CONFIG_VARIABLES[key]["value_cmd_false"])

                if CONFIG["config_process"].getboolean("value_script"):
                    if isinstance(CONFIG_VARIABLES[key]["value_script"], str):
                        if CONFIG_VARIABLES[key]["value_script"] != "":
                            state_script = True
                            if not execute_script(process_variable_cmd(CONFIG_VARIABLES[key]["value_script"], "value", VARIABLES_DATA[key])) and not error_ignore: error.append(key + " - value_script: " + CONFIG_VARIABLES[key]["value_script"])
                    if isinstance(CONFIG_VARIABLES[key]["value_script_true"], str):
                        if CONFIG_VARIABLES[key]["value_script_true"] != "" and val_to_bool(receive_json["data"][key]):
                            state_script = True
                            if not execute_script(process_variable_cmd(CONFIG_VARIABLES[key]["value_script_true"], "value", VARIABLES_DATA[key])) and not error_ignore: error.append(key + " - value_script_true: " + CONFIG_VARIABLES[key]["value_script_true"])
                    if isinstance(CONFIG_VARIABLES[key]["value_script_false"], str):
                        if CONFIG_VARIABLES[key]["value_script_false"] != "" and not val_to_bool(receive_json["data"][key]):
                            state_script = True
                            if not execute_script(process_variable_cmd(CONFIG_VARIABLES[key]["value_script_false"], "value", VARIABLES_DATA[key])) and not error_ignore: error.append(key + " - value_script_false: " + CONFIG_VARIABLES[key]["value_script_false"])

            if len(error) > 0:
                log("Process POST: " + ", ".join(error), LOG_ERROR)
                send_json["result"] = "0"
                send_json["msg"] = "\n".join(error)
            elif state_execute == True:
                send_json["result"] = "1"
                send_json["msg"] = config_get(CONFIG, "interface_messages", "post_ok_execute", "", lng_key)
            elif state_cmd == True:
                send_json["result"] = "1"
                send_json["msg"] = config_get(CONFIG, "interface_messages", "post_ok_cmd", "", lng_key)
            elif state_script == True:
                send_json["result"] = "1"
                send_json["msg"] = config_get(CONFIG, "interface_messages", "post_ok_script", "", lng_key)
            else:
                send_json["result"] = "1"
                send_json["msg"] = config_get(CONFIG, "interface_messages", "post_ok", "", lng_key)

            if send_json["msg"] == "": del send_json["msg"]

    for key in VARIABLES_SESSION:
        send_json["session"][key] = VARIABLES_SESSION[key]

    send = json.dumps(send_json)
    log("Process POST - Send: " + send, LOG_DEBUG)
    return send


##############################################################################################################
# Process DOWNLOAD


def process_download(receive):
    log("Process DOWNLOAD - Receive: " + receive, LOG_DEBUG)

    if receive != "":
        receive_json = json.loads(receive)

        if "data" in receive_json:
            if "app_config_user" in receive_json["data"] or "app_config_auto" in receive_json["data"]:
                if "app_config_user" in receive_json["data"]:
                    filename = receive_json["data"]["app_config_user"]
                if "app_config_auto" in receive_json["data"]:
                    filename = receive_json["data"]["app_config_auto"]
                with tarfile.open(PATH + "/tmp/tmp." + CONFIG["config"]["extension_transfer"], "w") as archive:
                    file = CONFIG["path"]["backup"] + "/" + filename + "." + CONFIG["config"]["extension"]
                    if os.path.isfile(file):
                        archive.add(file, arcname = filename + "." + CONFIG["config"]["extension"])
                    file = CONFIG["path"]["backup"] + "/" + filename + "." + CONFIG["config"]["extension"] + "." + CONFIG["config"]["extension_archive"]
                    if os.path.isfile(file):
                        archive.add(file, arcname = filename + "." + CONFIG["config"]["extension"] + "." + CONFIG["config"]["extension_archive"])

                return [PATH + "/tmp/tmp." + CONFIG["config"]["extension_transfer"], filename + "." + CONFIG["config"]["extension_transfer"]]
    return ["", ""]


##############################################################################################################
# Process UPLOAD


def process_upload(receive, file):
    log("Process UPLOAD - Receive: " + receive + " - File: " + file, LOG_DEBUG)

    send_json = defaultdict(dict)
    send_json["version"] = VERSION
    send_json["result"] = "0"

    if receive != "":
        receive_json = json.loads(receive)

        if "lng" not in receive_json or not CONFIG["main"].getboolean("lng_auto"):
            receive_json["lng"] = CONFIG["main"]["lng"]
        lng_key, lng_delimiter = build_lng(receive_json["lng"])

        if "uid" in receive_json and "cmd" in receive_json and "data" in receive_json:
            send_json["uid"] = receive_json["uid"]
            error = []

            with tarfile.open(file, "r") as archive:
                file_cfg = ""
                file_archive = ""
                for member in archive.getmembers():
                    if member.name.endswith("." + CONFIG["config"]["extension"]): file_cfg = member.name;
                    if member.name.endswith("." + CONFIG["config"]["extension_archive"]): file_archive = member.name;

                if file_cfg != "" and file_archive != "" and file_archive.startswith(file_cfg):
                    archive.extract(file_cfg, CONFIG["path"]["backup"] + "/")
                    archive.extract(file_archive, CONFIG["path"]["backup"] + "/")
                else:
                    error.append("File content")

            if len(error) > 0:
                send_json["result"] = "0"
                send_json["msg"] = "\n".join(error)
            else:
                send_json["result"] = "1"
                send_json["msg"] = config_get(CONFIG, "interface_messages", "post_ok_upload", "", lng_key)
                process_config_get(receive_json, send_json)

    os.remove(file)

    for key in VARIABLES_SESSION:
        send_json["session"][key] = VARIABLES_SESSION[key]

    send = json.dumps(send_json)
    log("Process UPLOAD - Send: " + send, LOG_DEBUG)
    return send




def process_upload_auth(file):
    file_ext = file.rsplit('.', 1)[1].lower()
    if file_ext != CONFIG["config"]["extension_transfer"]: return False
    return True


##############################################################################################################
# Process variable


def process_variable_merge(section="config_process"):
    global VARIABLES

    VARIABLES = defaultdict(dict)

    log("**** Process variable merge ****", LOG_DEBUG)

    if CONFIG[section].getboolean("variables_session"):
        if isinstance(VARIABLES_SESSION, dict):
            log("Merge: VARIABLES_SESSION", LOG_DEBUG)
            if CONFIG.has_option(section, "variables_session_prefix"):
                if CONFIG[section]["variables_session_prefix"] != "":
                    prefix = CONFIG[section]["variables_session_prefix"]
                    copy = {prefix + str(key): val for key, val in VARIABLES_SESSION.items()}
                    VARIABLES.update(copy)
                else:
                    VARIABLES.update(VARIABLES_SESSION)
            else:
                VARIABLES.update(VARIABLES_SESSION)

    if CONFIG[section].getboolean("variables_system"):
        if isinstance(VARIABLES_SYSTEM.data, dict):
            log("Merge: VARIABLES_SYSTEM", LOG_DEBUG)
            if CONFIG.has_option(section, "variables_system_prefix"):
                if CONFIG[section]["variables_system_prefix"] != "":
                    prefix = CONFIG[section]["variables_system_prefix"]
                    copy = {prefix + str(key): val for key, val in VARIABLES_SYSTEM.data.items()}
                    VARIABLES.update(copy)
                else:
                    VARIABLES.update(VARIABLES_SYSTEM.data)
            else:
                VARIABLES.update(VARIABLES_SYSTEM.data)

    if CONFIG[section].getboolean("variables_user"):
        if isinstance(VARIABLES_USER.data, dict):
            log("Merge: VARIABLES_USER", LOG_DEBUG)
            if CONFIG.has_option(section, "variables_user_prefix"):
                if CONFIG[section]["variables_user_prefix"] != "":
                    prefix = CONFIG[section]["variables_user_prefix"]
                    copy = {prefix + str(key): val for key, val in VARIABLES_USER.data.items()}
                    VARIABLES.update(copy)
                else:
                    VARIABLES.update(VARIABLES_USER.data)
            else:
                VARIABLES.update(VARIABLES_USER.data)

    if CONFIG[section].getboolean("variables_data"):
        if isinstance(VARIABLES_DATA, dict):
            log("Merge: VARIABLES_DATA", LOG_DEBUG)
            if CONFIG.has_option(section, "variables_data_prefix"):
                if CONFIG[section]["variables_data_prefix"] != "":
                    prefix = CONFIG[section]["variables_data_prefix"]
                    copy = {prefix + str(key): val for key, val in VARIABLES_DATA.items()}
                    VARIABLES.update(copy)
                else:
                    VARIABLES.update(VARIABLES_DATA)
            else:
                VARIABLES.update(VARIABLES_DATA)
    return True




def process_value_replace():
    global VARIABLES
    
    if CONFIG["config_process"].getboolean("value_replace"):
        log("**** Process value replace ****", LOG_DEBUG)
        for key in VARIABLES.keys():
            if isinstance(CONFIG_VARIABLES[key]["value_search"], str) and isinstance(CONFIG_VARIABLES[key]["value_replace"], str):
                if CONFIG_VARIABLES[key]["value_search"] != "":
                    value = VARIABLES[key]
                    VARIABLES[key] = VARIABLES[key].replace(CONFIG_VARIABLES[key]["value_search"], CONFIG_VARIABLES[key]["value_replace"])
                    log(key + ": Replace: " + CONFIG_VARIABLES[key]["value_search"] + " -> " + CONFIG_VARIABLES[key]["value_replace"], LOG_DEBUG)
                    log(key + ": " + value + " -> " + VARIABLES[key], LOG_DEBUG)




def process_value_regex():
    global VARIABLES
    
    if CONFIG["config_process"].getboolean("value_regex"):
        log("**** Process value regex ****", LOG_DEBUG)
        for key in VARIABLES.keys():
            if isinstance(CONFIG_VARIABLES[key]["value_regex_search"], str) and isinstance(CONFIG_VARIABLES[key]["value_regex_replace"], str):
                if CONFIG_VARIABLES[key]["value_regex_search"] != "" and CONFIG_VARIABLES[key]["value_regex_replace"] != "":
                    value = VARIABLES[key]
                    VARIABLES[key] = re.sub(CONFIG_VARIABLES[key]["value_regex_search"], CONFIG_VARIABLES[key]["value_regex_replace"], VARIABLES[key])
                    log(key + ": Regex: " + CONFIG_VARIABLES[key]["value_regex_search"] + " -> " + CONFIG_VARIABLES[key]["value_regex_replace"], LOG_DEBUG)
                    log(key + ": " + value + " -> " + VARIABLES[key], LOG_DEBUG)




def process_value_regex_match(key, value):
    if CONFIG["config_process"].getboolean("value_regex_match"):
        if isinstance(CONFIG_VARIABLES[key]["value_regex_match"], str):
            if CONFIG_VARIABLES[key]["value_regex_match"] != "" and value != "":
                if re.match(r''+ CONFIG_VARIABLES[key]["value_regex_match"], value):
                    return True
                else:
                    return False
    return True




def process_value_convert():
    global VARIABLES
    
    if CONFIG["config_process"].getboolean("value_convert"):
        log("**** Process value convert ****", LOG_DEBUG)
        CONVERT = convert_class()
        for key in VARIABLES.keys():
            if isinstance(CONFIG_VARIABLES[key]["value_convert"], str):
                if CONFIG_VARIABLES[key]["value_convert"] != "":
                    value = VARIABLES[key]
                    VARIABLES[key] = CONVERT.run(CONFIG_VARIABLES[key]["value_convert"], VARIABLES[key])
                    log(key + ": Convert: " + CONFIG_VARIABLES[key]["value_convert"], LOG_DEBUG)
                    log(key + ": " + value + " -> " + VARIABLES[key], LOG_DEBUG)




def process_variable(text):
    if CONFIG["config_process"].getboolean("variable") and CONFIG.has_option("config", "delimiter_variable"):
        if CONFIG["config"]["delimiter_variable"] != "":
            log("**** Process variable ****", LOG_DEBUG)
            for variables_key in VARIABLES.keys():
                if isinstance(VARIABLES[variables_key], str):
                    text = text.replace(CONFIG["config"]["delimiter_variable"] + variables_key + CONFIG["config"]["delimiter_variable"], VARIABLES[variables_key])
                else:
                    text = text.replace(CONFIG["config"]["delimiter_variable"] + variables_key + CONFIG["config"]["delimiter_variable"], "")
    return text




def process_variable_cmd(text, key="", value=""):
    if CONFIG["config_process"].getboolean("variable_cmd") and CONFIG.has_option("config", "delimiter_variable_cmd"):
        if CONFIG["config"]["delimiter_variable_cmd"] != "":
            log("**** Process variable cmd ****", LOG_DEBUG)
            if key != "":
                if not isinstance(value, str): value = ""
                text = text.replace(CONFIG["config"]["delimiter_variable_cmd"] + key + CONFIG["config"]["delimiter_variable_cmd"], value)
            for variables_key in VARIABLES.keys():
                if isinstance(VARIABLES[variables_key], str):
                    text = text.replace(CONFIG["config"]["delimiter_variable_cmd"] + variables_key + CONFIG["config"]["delimiter_variable_cmd"], VARIABLES[variables_key])
                else:
                    text = text.replace(CONFIG["config"]["delimiter_variable_cmd"] + variables_key + CONFIG["config"]["delimiter_variable_cmd"], "")
    return text




def process_if(text):
    if CONFIG["config_process"].getboolean("if_standard") and CONFIG.has_option("config", "delimiter_if_standard"):
        if CONFIG["config"]["delimiter_if_standard"] != "":
            log("**** Process if standard ****", LOG_DEBUG)
            text_search = "\n" + text + "\n"
            regex = re.findall(r'[^'+CONFIG["config"]["delimiter_if_standard"][0]+']('+CONFIG["config"]["delimiter_if_standard"]+'([^\s][^'+CONFIG["config"]["delimiter_if_standard"][0]+'].*[^\s])'+CONFIG["config"]["delimiter_if_standard"]+'((\n|.)*?)'+CONFIG["config"]["delimiter_if_standard"]+')[^'+CONFIG["config"]["delimiter_if_standard"][0]+']', text_search)
            log(regex, LOG_EXTREME)
            for match in regex:
                if group := re.match(r'([^\s]+)(\s+)?(==|!=)(\s+)?[\'\"]?([^\s\'\"]+)[\'\"]?', match[1]):
                    log(group, LOG_EXTREME)
                    cmd = match[1]
                    cmd = re.sub(r' && ', r' and ', cmd)
                    cmd = re.sub(r' \|\| ', r' or ', cmd)
                    cmd = re.sub(r'([^\s(]+)(\s+)?(==|!=)(\s+)?[\'\"]?([^\s\'\")]+)[\'\"]?', r'VARIABLES["\1"] \3 "\5"', cmd)
                    log("Try if: " + cmd, LOG_DEBUG)
                    try:
                        if eval(cmd):
                            replace = match[2]
                            replace = replace.lstrip()
                            replace = replace.rstrip()
                            text = text.replace(match[0], replace)
                            log("If matched - Used text: " + replace, LOG_DEBUG)
                            continue
                        else:
                            log("If not matched", LOG_DEBUG)
                    except Exception as e:
                        log("If error: " + e, LOG_ERROR)
                        continue

    if CONFIG["config_process"].getboolean("if_regex") and CONFIG.has_option("config", "delimiter_if_regex"):
        if CONFIG["config"]["delimiter_if_regex"] != "":
            log("**** Process if regex ****", LOG_DEBUG)
            text_search = "\n" + text + "\n"
            regex = re.findall(r'[^'+CONFIG["config"]["delimiter_if_regex"][0]+']('+CONFIG["config"]["delimiter_if_regex"]+'([^\s][^'+CONFIG["config"]["delimiter_if_regex"][0]+'].*[^\s])'+CONFIG["config"]["delimiter_if_regex"]+'((\n|.)*?)'+CONFIG["config"]["delimiter_if_regex"]+')[^'+CONFIG["config"]["delimiter_if_regex"][0]+']', text_search)
            log(regex, LOG_EXTREME)
            for match in regex:
                if group := re.match(r'([^\s]+)(\s+)?(==)(\s+)?([\S]+)', match[1]):
                    log(group, LOG_EXTREME)
                    cmd = match[1]
                    cmd = re.sub(r' && ', r' and ', cmd)
                    cmd = re.sub(r' \|\| ', r' or ', cmd)
                    cmd = re.sub(r'([^\s(]+)(\s+)?(==)(\s+)?([\S]+)', r're.match(r"\5", VARIABLES["\1"])', cmd)
                    log("Try if: " + cmd, LOG_DEBUG)
                    try:
                        if eval(cmd):
                            replace = match[2]
                            replace = replace.lstrip()
                            replace = replace.rstrip()
                            text = text.replace(match[0], replace)
                            log("If matched - Used text: " + replace, LOG_DEBUG)
                            continue
                        else:
                            log("If not matched", LOG_DEBUG)
                    except Exception as e:
                        log("If error: " + e, LOG_ERROR)
                        continue
    return text




def process_cleanup(text):
    if CONFIG["config_process"].getboolean("if_standard_cleanup") and CONFIG.has_option("config", "delimiter_if_standard"):
        if CONFIG["config"]["delimiter_if_standard"] != "":
            log("**** Process cleanup if standard ****", LOG_DEBUG)
            text_search = "\n" + text + "\n"
            regex = re.findall(r'[^'+CONFIG["config"]["delimiter_if_standard"][0]+']('+CONFIG["config"]["delimiter_if_standard"]+'([^\s][^'+CONFIG["config"]["delimiter_if_standard"][0]+'].*[^\s])'+CONFIG["config"]["delimiter_if_standard"]+'((\n|.)*?)'+CONFIG["config"]["delimiter_if_standard"]+')[^'+CONFIG["config"]["delimiter_if_standard"][0]+']', text_search)
            log(regex, LOG_EXTREME)
            for match in regex:
                if CONFIG["config_process"]["if_standard_cleanup_type"] == "comment" and CONFIG["config_process"]["if_standard_cleanup_value"] != "":
                    replace = CONFIG["config_process"]["if_standard_cleanup_value"] + match[0].replace("\n","\n" + CONFIG["config_process"]["if_standard_cleanup_value"])
                    text = text.replace(match[0], replace)
                else:
                    text = text.replace(match[0], "")
                log("Cleanup: " + match[0], LOG_DEBUG)

    if CONFIG["config_process"].getboolean("if_regex_cleanup") and CONFIG.has_option("config", "delimiter_if_regex"):
        if CONFIG["config"]["delimiter_if_regex"] != "":
            log("**** Process cleanup if regex ****", LOG_DEBUG)
            text_search = "\n" + text + "\n"
            regex = re.findall(r'[^'+CONFIG["config"]["delimiter_if_regex"][0]+']('+CONFIG["config"]["delimiter_if_regex"]+'([^\s][^'+CONFIG["config"]["delimiter_if_regex"][0]+'].*[^\s])'+CONFIG["config"]["delimiter_if_regex"]+'((\n|.)*?)'+CONFIG["config"]["delimiter_if_regex"]+')[^'+CONFIG["config"]["delimiter_if_regex"][0]+']', text_search)
            log(regex, LOG_EXTREME)
            for match in regex:
                if CONFIG["config_process"]["if_regex_cleanup_type"] == "comment" and CONFIG["config_process"]["if_regex_cleanup_value"] != "":
                    replace = CONFIG["config_process"]["if_regex_cleanup_value"] + match[0].replace("\n","\n" + CONFIG["config_process"]["if_regex_cleanup_value"])
                    text = text.replace(match[0], replace)
                else:
                    text = text.replace(match[0], "")
                log("Cleanup: " + match[0], LOG_DEBUG)

    if CONFIG["config_process"].getboolean("variable_cleanup") and CONFIG.has_option("config", "delimiter_variable"):
        if CONFIG["config"]["delimiter_variable"] != "":
            log("**** Process cleanup variable ****", LOG_DEBUG)
            text_search = "\n" + text + "\n"
            regex = re.findall(r''+CONFIG["config"]["delimiter_variable"]+'[a-zA-z0-9_\-]+'+CONFIG["config"]["delimiter_variable"], text_search)
            log(regex, LOG_EXTREME)
            for match in regex:
                text = text.replace(match[0], "")
                log("Cleanup: " + match[0], LOG_DEBUG)

    return text


##############################################################################################################
# Process config


def process_config_get(receive_json, send_json):
    if CONFIG["config"].getboolean("backup_user"):
        array = []
        files = sorted(glob.glob(CONFIG["path"]["backup"] + "/*" + CONFIG["config"]["backup_user_name"] + "." + CONFIG["config"]["extension"], recursive=False))
        for file in files:
            if not os.path.basename(file).endswith(CONFIG["config"]["backup_auto_name"] + "." + CONFIG["config"]["extension"]):
                filename = os.path.basename(file)
                filename = filename.replace(CONFIG["config"]["backup_user_name"] + "." + CONFIG["config"]["extension"], "")
                array.append(filename + "=" + filename)
        send_json["data"]["app_config_user_data"] = ";".join(array)

    if CONFIG["config"].getboolean("backup_auto"):
        array = []
        files = sorted(glob.glob(CONFIG["path"]["backup"] + "/*" + CONFIG["config"]["backup_auto_name"] + "." + CONFIG["config"]["extension"], recursive=False))
        for file in files:
            filename = os.path.basename(file)
            filename = filename.replace(CONFIG["config"]["backup_auto_name"] + "." + CONFIG["config"]["extension"], "")
            filename = filename.replace("_", " ")
            file = os.path.basename(file)
            file = file.replace("." + CONFIG["config"]["extension"], "")
            array.append(file + "=" + filename)
        send_json["data"]["app_config_auto_data"] = ";".join(array)

    return True




def process_config_set(receive_json, send_json):
    global VARIABLES_DATA

    require = False

    if CONFIG["config"].getboolean("backup_user") and "app_config_user_text" in receive_json["data"] and "app_config_user_save" in receive_json["data"]:
        file = CONFIG["path"]["backup"] + "/" + receive_json["data"]["app_config_user_text"] + CONFIG["config"]["backup_user_name"] + "." + CONFIG["config"]["extension"]

        with open(file, "w") as outfile:
            json.dump(VARIABLES_DATA, outfile)

        if CONFIG["config"].getboolean("backup_user_files"):
            with tarfile.open(file + "." + CONFIG["config"]["extension_archive"], "w") as archive:
                for page in CONFIG_FILES.keys():
                   for key in CONFIG_FILES[page]["files"].keys():
                       if isinstance(CONFIG_FILES[page]["files_type"][key], str):
                           if CONFIG_FILES[page]["files_type"][key] in CONFIG["config"]["backup_user_files_exclude_type"]:
                               continue
                       if CONFIG["main"].getboolean("mode_test"):
                           file = CONFIG["path"]["mode_test"] + CONFIG_FILES[page]["files"][key]
                       else:
                           file = CONFIG_FILES[page]["files"][key]
                       if os.path.isfile(file):
                           archive.add(file)

        process_config_get(receive_json, send_json)

    if CONFIG["config"].getboolean("backup_user") and "app_config_user" in receive_json["data"] and "app_config_user_delete" in receive_json["data"]:
        files = sorted(glob.glob(CONFIG["path"]["backup"] + "/" + receive_json["data"]["app_config_user"] + CONFIG["config"]["backup_user_name"] + "." + CONFIG["config"]["extension"] + "*", recursive=False))
        for file in files:
            os.remove(file)
        process_config_get(receive_json, send_json)

    if CONFIG["config"].getboolean("backup_user") and "app_config_user_delete_all" in receive_json["data"]:
        files = sorted(glob.glob(CONFIG["path"]["backup"] + "/*" + CONFIG["config"]["backup_user_name"] + "." + CONFIG["config"]["extension"] + "*", recursive=False))
        for file in files:
            os.remove(file)
        process_config_get(receive_json, send_json)

    if CONFIG["config"].getboolean("backup_user") and "app_config_user" in receive_json["data"] and "app_config_user_restore" in receive_json["data"]:
        file = CONFIG["path"]["backup"] + "/" + receive_json["data"]["app_config_user"] + CONFIG["config"]["backup_user_name"] + "." + CONFIG["config"]["extension"]
        VARIABLES_DATA = {}
        receive_json["data"] = {}
        receive_json["data"]["app_config_files"] = file
        receive_json["data"]["app_config_user_restore"] = ""
        send_json["data"] = {}
        if os.path.isfile(file):
            with open(file) as outfile:
                data = json.load(outfile)
                for key in data.keys():
                    VARIABLES_DATA[key] = data[key]
                    receive_json["data"][key] = data[key]
                    send_json["data"][key] = data[key]
                require = True

    if CONFIG["config"].getboolean("backup_auto") and "app_config_auto" in receive_json["data"] and "app_config_auto_delete" in receive_json["data"]:
        files = sorted(glob.glob(CONFIG["path"]["backup"] + "/" + receive_json["data"]["app_config_auto"] + "." + CONFIG["config"]["extension"] + "*", recursive=False))
        for file in files:
            os.remove(file)
        process_config_get(receive_json, send_json)

    if CONFIG["config"].getboolean("backup_auto") and "app_config_auto_delete_all" in receive_json["data"]:
        files = sorted(glob.glob(CONFIG["path"]["backup"] + "/*" + CONFIG["config"]["backup_auto_name"] + "." + CONFIG["config"]["extension"] + "*", recursive=False))
        for file in files:
            os.remove(file)
        process_config_get(receive_json, send_json)

    if CONFIG["config"].getboolean("backup_auto") and "app_config_auto" in receive_json["data"] and "app_config_auto_restore" in receive_json["data"]:
        file = CONFIG["path"]["backup"] + "/" + receive_json["data"]["app_config_auto"] + "." + CONFIG["config"]["extension"]
        VARIABLES_DATA = {}
        receive_json["data"] = {}
        receive_json["data"]["app_config_files"] = file
        receive_json["data"]["app_config_auto_restore"] = ""
        send_json["data"] = {}
        if os.path.isfile(file):
            with open(file) as outfile:
                data = json.load(outfile)
                for key in data.keys():
                    VARIABLES_DATA[key] = data[key]
                    receive_json["data"][key] = data[key]
                    send_json["data"][key] = data[key]
                require = True

    if CONFIG["config"].getboolean("backup_factory") and "app_config_factory_restore" in receive_json["data"]:
        file = CONFIG["path"]["backup"] + "/" + CONFIG["config"]["backup_factory_name"] + "." + CONFIG["config"]["extension"]
        VARIABLES_DATA = {}
        receive_json["data"] = {}
        receive_json["data"]["app_config_files"] = file
        receive_json["data"]["app_config_factory_restore"] = ""
        send_json["data"] = {}
        if os.path.isfile(file):
            with open(file) as outfile:
                data = json.load(outfile)
                for key in data.keys():
                    VARIABLES_DATA[key] = data[key]
                    receive_json["data"][key] = data[key]
                    send_json["data"][key] = data[key]
                require = True
        #if "lng" not in receive_json or not CONFIG["main"].getboolean("lng_auto"):
        #    receive_json["lng"] = CONFIG["main"]["lng"]
        #build_data(receive_json["lng"])
        #receive_json["data"] = {}
        #receive_json["data"]["app_config_factory_restore"] = "True"
        #send_json["data"] = {}
        #for key in VARIABLES_DATA:
        #    send_json["data"][key] = VARIABLES_DATA[key]

    if require:
        if CONFIG["config_process"].getboolean("require_acknowledge"):
            if CONFIG["config"].getboolean("backup_require_acknowledge"): VARIABLES_SESSION["require_acknowledge"] = True

        if CONFIG["config_process"].getboolean("require_reboot"):
            if CONFIG["config"].getboolean("backup_require_reboot"): VARIABLES_SESSION["require_reboot"] = True

        if CONFIG["config_process"].getboolean("require_reload"):
            if CONFIG["config"].getboolean("backup_require_reload"): VARIABLES_SESSION["require_reload"] = True

    return True


##############################################################################################################
# Process software


def process_software_get(receive_json, send_json):
    if "app_software" not in receive_json["data_live"]: return True
    log("Process Software GET", LOG_EXTREME)
    return True




def process_software_set(receive_json, send_json):
    log("Process Software SET", LOG_EXTREME)
    return True




def process_software_require(config):
    if config != "":
        if re.match(r'([^\s(]+)(\s+)?(==|!=)(\s+)?[\'\"]?([^\s\'\")]+)[\'\"]?', config):
            config = re.sub(r' && ', r' and ', config)
            config = re.sub(r' \|\| ', r' or ', config)
            config = re.sub(r'([^\s(]+)(\s+)?(==|!=)(\s+)?[\'\"]?([^\s\'\")]+)[\'\"]?', r'"\5" \3 VARIABLES_SOFTWARE["\1"]', config)
            config = re.sub(r' == ', r' in ', config)
            config = re.sub(r' != ', r' not in ', config)
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
                    if x in VARIABLES_SOFTWARE["software"]: return False
                else:
                    if x not in VARIABLES_SOFTWARE["software"]: return False
    return True


##############################################################################################################
# Process wizard


def process_wizard_get(receive_json, send_json):
    if "app_wizard" not in receive_json["data_live"]: return True
    log("Process Wizard GET", LOG_EXTREME)

    if CONFIG["wizard_process"].getboolean("system_load"):
        send_json["data_live"]["app_wizard_active_cpu"] = str(round(psutil.cpu_percent()))
        send_json["data_live"]["app_wizard_active_memory"] = str(round(psutil.virtual_memory().percent))
        send_json["data_live"]["app_wizard_active_swap"] = str(round(psutil.swap_memory().percent))
        send_json["data_live"]["app_wizard_active_disk"] = str(round(psutil.disk_usage('/').percent))

        net_io = psutil.net_io_counters()
        time_current = time.time()
        if hasattr(process_wizard_get, "net_time"):
            net_recv = (net_io.bytes_recv - process_wizard_get.net_bytes_recv) / (time_current - process_wizard_get.net_time)
            for unit in ['', 'K', 'M', 'G', 'T', 'P']:
                if net_recv < 1024:
                    net_recv = f"{net_recv:.2f}{unit}B/s"
                    break;
                net_recv /= 1024
            net_sent = (net_io.bytes_sent - process_wizard_get.net_bytes_sent) / (time_current - process_wizard_get.net_time)
            for unit in ['', 'K', 'M', 'G', 'T', 'P']:
                if net_sent < 1024:
                    net_sent = f"{net_sent:.2f}{unit}B/s"
                    break;
                net_sent /= 1024
            send_json["data_live"]["app_wizard_active_network_download"] = net_recv
            send_json["data_live"]["app_wizard_active_network_upload"] = net_sent
            send_json["data_live"]["app_wizard_active_network"] = "🡇" + net_recv + " 🡅" + net_sent
        else:
            send_json["data_live"]["app_wizard_active_network_download"] = ""
            send_json["data_live"]["app_wizard_active_network_upload"] = ""
            send_json["data_live"]["app_wizard_active_network"] = ""
        process_wizard_get.net_time = time_current
        process_wizard_get.net_bytes_recv = net_io.bytes_recv
        process_wizard_get.net_bytes_sent = net_io.bytes_sent

    if "wizard_execute" in VARIABLES_SESSION and "wizard_execute_current" in VARIABLES_SESSION:
        if not "data" in receive_json: receive_json["data"] = {}
        receive_json["data"]["app_wizard_run"] = VARIABLES_SESSION["wizard_execute"]
        receive_json["data"]["app_wizard_next"] = VARIABLES_SESSION["wizard_execute_current"]
        process_wizard_set(receive_json, send_json)
        VARIABLES_SESSION.pop("wizard_execute", None)
        VARIABLES_SESSION.pop("wizard_execute_current", None)
        try:
            os.remove(CONFIG["path"]["config"] + "/session_current." + CONFIG["config"]["extension"])
        except OSError:
            None
        return True

    global CONFIG_WIZARD
    global TERMINAL

    if not CONFIG_WIZARD: return True
    if not TERMINAL: return True

    output, state = TERMINAL.get()

    if "lng" not in receive_json or not CONFIG["main"].getboolean("lng_auto"):
        receive_json["lng"] = CONFIG["main"]["lng"]
    lng_key, lng_delimiter = build_lng(receive_json["lng"])

    if CONFIG["wizard_process"].getboolean("log_expert_output") and (not CONFIG["wizard_process"].getboolean("log_expert_output_terminal") or output != ""):
        log_file = config_get(CONFIG_WIZARD, "execute", "log", "", lng_key)
        if log_file != "":
            try:
                file_time = str(os.path.getmtime(log_file))
                if file_time != CONFIG_WIZARD["tmp"]["log_time"]:
                    CONFIG_WIZARD["tmp"]["log_time"] = file_time
                    file_handler = open(log_file)
                    file_string = file_handler.read()
                    file_handler.close()
                    if file_string != "":
                        send_json["data_live"]["app_wizard_active_log_expert"] = re.sub(r'^\s+|\s+$', '', file_string.replace(CONFIG_WIZARD["tmp"]["log"], "")) + "\n"
                        CONFIG_WIZARD["tmp"]["log"] = file_string
                        if CONFIG["wizard_process"].getboolean("output_replace_ansi"):
                            ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
                            send_json["data_live"]["app_wizard_active_log_expert"] = ansi_escape.sub('', send_json["data_live"]["app_wizard_active_log_expert"])
                            size = config.getint("wizard_process", "log_expert_output_max_lenght")
                            if size > 0:
                                send_json["data_live"]["app_wizard_active_log_expert"] = send_json["data_live"]["app_wizard_active_log_expert"][-size]
                            size = config.getint("wizard_process", "log_expert_output_max_lines")
                            if size > 0:
                                send_json["data_live"]["app_wizard_active_log_expert"] = re.sub(r'((.*(\n|\r|\r\n)){'+size+'})', '', send_json["data_live"]["app_wizard_active_log_expert"])
            except:
                None

    if output == "": return True

    log("Output - RAW:" + output, LOG_EXTREME)
    if LOG_LEVEL >= LOG_EXTREME: send_json["log"]["output_raw"] = output
    if LOG_LEVEL >= LOG_EXTREME: send_json["log"]["state"] = state

    if CONFIG["wizard_process"].getboolean("log_output"):
        output_log = ""
        if CONFIG["wizard_process"]["log_mode"] == "raw":
            output_log = output
        elif CONFIG["wizard_process"]["log_mode"] == "ansi":
            output_log = output
            ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
            output_log = ansi_escape.sub('', output_log)

    state_running = True
    if CONFIG["wizard_process"].getboolean("output_state"):
        if CONFIG.has_option("wizard_process", "output_state_regex"):
            if re.search(CONFIG["wizard_process"]["output_state_regex"], output):
                state_running = False
    if LOG_LEVEL >= LOG_EXTREME: send_json["log"]["state_running"] = state_running

    if CONFIG["wizard_process"].getboolean("output_replace_cmd"):
        output = re.sub(r'\u001b\[\?2004h.*?#\s', '', output)
        output = output.replace("\u001b[?2004l", "")
        #output = re.sub(r'.*@.*#', '', output)
        if CONFIG_WIZARD["tmp"]["cmd"] != "":
            while output.startswith(CONFIG_WIZARD["tmp"]["cmd"]):
                output = output.replace(CONFIG_WIZARD["tmp"]["cmd"], "", 1)
            CONFIG_WIZARD["tmp"]["cmd"] = ""

    state_append = False
    if CONFIG["wizard_process"].getboolean("output_append"):
        if CONFIG.has_option("wizard_process", "output_append_regex"):
            if re.search(CONFIG["wizard_process"]["output_append_regex"], output):
                state_append = True
    if LOG_LEVEL >= LOG_EXTREME: send_json["log"]["state_append"] = state_append

    if CONFIG["wizard_process"].getboolean("output_replace_color"):
        output = re.sub(r'\u001b\[0m', '</span>', output)
        regex = re.findall(r'(\u001b\[0?;?(\d{1,2})m)', output)
        for match in regex:
            if group := re.search(r''+match[1]+'\s?=\s?(\w+)', CONFIG["wizard_process"]["output_color"]):
                output = output.replace(match[0], "<span style='color:" + group[1] + "'>")
            else:
                output = output.replace(match[0], "<span>")

    if CONFIG["wizard_process"].getboolean("output_replace_ansi"):
        ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
        output = ansi_escape.sub('', output)
        if LOG_LEVEL >= LOG_EXTREME: send_json["log"]["output_replace_ansi"] = output

    if CONFIG["wizard_process"].getboolean("output_replace_log"):
        output = re.sub(r'[\[\(]\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}[\]\)]', '', output)

    if CONFIG["wizard_process"].getboolean("output_replace_whitespace"):
        output = re.sub(r'(\r)+(\n)+', '\n', output)
        output = re.sub(r'(\n)+((\s+)?\r)+', '\n', output)
        output = re.sub(r'((\s+)?\r)+', '\n', output)
        output = re.sub(r'^\s+|\s+$', '', output)
        output = re.sub(r'^ +| +$', '', output, flags=re.M)

    if CONFIG["wizard_process"].getboolean("output_replace_double_lines"):
        output = re.sub(r'^(.*)(\r?\n\1)+$', r'\1', output, flags=re.M)

    if CONFIG["wizard_process"].getboolean("output_replace_special_characters"):
        output = output.replace(" :", ":")
        output = output.replace("?:", "?")

    input_generate = ""
    if CONFIG["wizard_process"]["input_generate_mode"] == "raw":
        input_generate = output

    if CONFIG["wizard_process"].getboolean("output_replace_unnecessary_characters"):
        output = re.sub(r'^[\-\_]+|[\-\_]+$', '', output)
        output = re.sub(r'^[^a-zA-Z0-9]$', '', output, flags=re.M)
        output = re.sub(r'^#\?$', '', output, flags=re.M)
        output = re.sub(r'\?\s?:', '', output)

    section = "output_replace"
    if CONFIG["wizard_process"].getboolean(section):
        if CONFIG_WIZARD.has_section(section+lng_key):
            section = section+lng_key
            for (key_search, val_search) in CONFIG_WIZARD.items(section):
                if key_search.endswith("search"):
                    key_replace = key_search.replace("search", "replace")
                    if CONFIG_WIZARD.has_option(section, key_replace):
                        val_search = val_search.replace("\\n", "\n")
                        val_replace = CONFIG_WIZARD[section][key_replace]
                        val_replace = val_replace.replace("\\n", "\n")
                        output = output.replace(val_search, val_replace)
        elif CONFIG_WIZARD.has_section(section):
            for (key_search, val_search) in CONFIG_WIZARD.items(section):
                if key_search.endswith("search"):
                    key_replace = key_search.replace("search", "replace")
                    if CONFIG_WIZARD.has_option(section, key_replace):
                        val_search = val_search.replace("\\n", "\n")
                        val_replace = CONFIG_WIZARD[section][key_replace]
                        val_replace = val_replace.replace("\\n", "\n")
                        output = output.replace(val_search, val_replace)

    section = "output_regex"
    if CONFIG["wizard_process"].getboolean(section):
        if CONFIG_WIZARD.has_section(section+lng_key):
            section = section+lng_key
            for (key_search, val_search) in CONFIG_WIZARD.items(section):
                if key_search.endswith("search"):
                    key_replace = key_search.replace("search", "replace")
                    if CONFIG_WIZARD.has_option(section, key_replace):
                        output = re.sub(val_search, CONFIG_WIZARD[section][key_replace], output)
        elif CONFIG_WIZARD.has_section(section):
            for (key_search, val_search) in CONFIG_WIZARD.items(section):
                if key_search.endswith("search"):
                    key_replace = key_search.replace("search", "replace")
                    if CONFIG_WIZARD.has_option(section, key_replace):
                        output = re.sub(val_search, CONFIG_WIZARD[section][key_replace], output)

    if CONFIG["wizard_process"].getboolean("output_replace_lng"):
        if CONFIG_WIZARD.has_section("tmp_files_lng"):
            replace_lng = []
            for (key, val) in CONFIG_WIZARD.items("tmp_files_lng"):
                file_handler = open(val)
                file_string = "\n\n" + file_handler.read() + "\n\n"
                file_handler.close() 
                if CONFIG["config"]["delimiter_lng"] != "":
                    regex = re.findall(r'^(?!'+CONFIG["config"]["delimiter_lng"]+')(.*)\n^(?!'+CONFIG["config"]["delimiter_lng"]+')(.*)\n\n', file_string, flags=re.M)
                else:
                    regex = re.findall(r'(.*)\n(.*)\n\n', file_string)
                for match in regex:
                    if match[0] != "" and match[1] != "":
                        replace_lng.append([match[0].replace("\\n", "\n"), match[1].replace("\\n", "\n")])
            replace_lng_sorted = sorted(replace_lng, key=lambda l: len(l[0]), reverse=True)
            for key, val in replace_lng_sorted:
                output = output.replace(key, val)

    if CONFIG["wizard_process"].getboolean("output_replace_whitespace"):
        output = re.sub(r'^\s+|\s+$', '', output)
        output = re.sub(r'^ +| +$', '', output, flags=re.M)

    log("Output - Replace:" + output, LOG_EXTREME)
    if LOG_LEVEL >= LOG_EXTREME: send_json["log"]["output_replace_end"] = output

    send_json["data_live"]["app_wizard_active_log"] = ""
    if output != "":
        if CONFIG["wizard_process"].getboolean("log_input") and CONFIG_WIZARD["tmp"]["cmd_log"] != "":
                send_json["data_live"]["app_wizard_active_log"] += '<span class="log_input">' + CONFIG_WIZARD["tmp"]["cmd_log"] + "</span>\n"
        if CONFIG["wizard_process"].getboolean("log_output"):
            if CONFIG["wizard_process"]["log_mode"] == "replace":
                output_log = output
            if output_log != "":
                send_json["data_live"]["app_wizard_active_log"] += output_log + "\n"

    CONFIG_WIZARD["tmp"]["cmd_log"] = ""

    if state > 0:
        state = "error"
        log("State: Error", LOG_EXTREME)

        if CONFIG["wizard_process"].getboolean("require_reboot_now") and config_getboolean(CONFIG_WIZARD, "main", "require_reboot_now", False, lng_key):
            output = output + "\n" + config_get(CONFIG, "wizard_interface", "output_reboot", "", lng_key)
            send_json["config_live"]["app_wizard_active_input_right"] = build_interface_content(json.loads('{"0":{"type":"submit_confirm","name":"app_wizard_reboot","tabindex":"20","autofocus":"true","content":"' + config_get(CONFIG, "wizard_interface", "button_reboot", "Reboot", lng_key) + '","class_content":"btn-success","message":"' + config_get(CONFIG, "wizard_interface", "message_reboot", "Reboot now?", lng_key) + '","transmit_empty":"True","value_view_toggle":"app_wizard_active_input,app_wizard_active_input_left,app_wizard_active_input_expert","cmd_success":"reconnect"}}'))
            send_json["config_live"]["app_wizard_active_input_left"] = ""
        else:
            send_json["config_live"]["app_wizard_active_input_right"] = process_wizard_group_input(CONFIG_WIZARD["tmp"]["execute_group"], CONFIG_WIZARD["tmp"]["execute_current"], lng_key)
            if send_json["config_live"]["app_wizard_active_input_right"] == "":
                send_json["config_live"]["app_wizard_active_input_left"] = {}
                if config_getboolean(CONFIG_WIZARD, "input", "restart_error", False, lng_key):
                    send_json["config_live"]["app_wizard_active_input_left"]["0"] = build_interface_content(json.loads('{"type":"submit_confirm","name":"app_wizard_restart","tabindex":"32","content":"' + config_get(CONFIG, "wizard_interface", "button_restart_error", "Restart", lng_key) + '","class_content":"btn-secondary","message":"' + config_get(CONFIG, "wizard_interface", "message_restart_error", "Restart?", lng_key) + '","transmit_empty":"True"}'))
            else:
                send_json["config_live"]["app_wizard_active_input_left"] = {}
                if config_getboolean(CONFIG_WIZARD, "input", "restart_error", False, lng_key):
                    send_json["config_live"]["app_wizard_active_input_left"]["0"] = build_interface_content(json.loads('{"type":"submit_confirm","name":"app_wizard_restart","tabindex":"32","content":"' + config_get(CONFIG, "wizard_interface", "button_restart_error", "Restart", lng_key) + '","class_content":"btn-secondary","message":"' + config_get(CONFIG, "wizard_interface", "message_restart_error", "Restart?", lng_key) + '","transmit_empty":"True"}'))
                if config_getboolean(CONFIG_WIZARD, "input", "abort", True, lng_key):
                    send_json["config_live"]["app_wizard_active_input_left"]["1"] = build_interface_content(json.loads('{"type":"submit_confirm","name":"app_wizard_abort","tabindex":"31","content":"' + config_get(CONFIG, "wizard_interface", "button_abort", "Abort", lng_key) + '","class_content":"btn-secondary","message":"' + config_get(CONFIG, "wizard_interface", "message_abort", "Abort?", lng_key) + '","transmit_empty":"True"}'))
                if config_getboolean(CONFIG_WIZARD, "input", "abort_group", False, lng_key):
                    send_json["config_live"]["app_wizard_active_input_left"]["2"] = build_interface_content(json.loads('{"type":"submit_confirm","name":"app_wizard_abort_group","tabindex":"30","content":"' + config_get(CONFIG, "wizard_interface", "button_abort_group", "Abort all", lng_key) + '","class_content":"btn-secondary","message":"' + config_get(CONFIG, "wizard_interface", "message_abort_group", "Abort all?", lng_key) + '","transmit_empty":"True"}'))

        send_json["config_live"]["app_wizard_active_input"] = ""
        send_json["config_live"]["app_wizard_active_input_expert"] = ""
        send_json["data_live"]["app_wizard_active_status"] = "footer abort"
        if CONFIG["wizard_process"].getboolean("log_state"):
            send_json["data_live"]["app_wizard_active_log"] += '\n<span class="' + config_get(CONFIG, "wizard_interface", "class_error", "", lng_key) + '">' + config_get(CONFIG, "wizard_interface", "log_error", "", lng_key) + "</span>"

    elif state_running == False:
        state = "end"
        log("State: End", LOG_EXTREME)

        if CONFIG["wizard_process"].getboolean("require_reboot_now") and config_getboolean(CONFIG_WIZARD, "main", "require_reboot_now", False, lng_key):
            output = output + "\n" + config_get(CONFIG, "wizard_interface", "output_reboot", "", lng_key)
            send_json["config_live"]["app_wizard_active_input_right"] = build_interface_content(json.loads('{"0":{"type":"submit_confirm","name":"app_wizard_reboot","tabindex":"20","autofocus":"true","content":"' + config_get(CONFIG, "wizard_interface", "button_reboot", "Reboot", lng_key) + '","class_content":"btn-success","message":"' + config_get(CONFIG, "wizard_interface", "message_reboot", "Reboot now?", lng_key) + '","transmit_empty":"True","value_view_toggle":"app_wizard_active_input,app_wizard_active_input_left,app_wizard_active_input_expert","cmd_success":"reconnect"}}'))
            send_json["config_live"]["app_wizard_active_input_left"] = ""
        else:
            send_json["config_live"]["app_wizard_active_input_right"] = process_wizard_group_input(CONFIG_WIZARD["tmp"]["execute_group"], CONFIG_WIZARD["tmp"]["execute_current"], lng_key)
            if send_json["config_live"]["app_wizard_active_input_right"] == "":
                send_json["config_live"]["app_wizard_active_input_left"] = {}
                if config_getboolean(CONFIG_WIZARD, "input", "restart_success", False, lng_key):
                    send_json["config_live"]["app_wizard_active_input_left"]["0"] = build_interface_content(json.loads('{"type":"submit_confirm","name":"app_wizard_restart","tabindex":"32","content":"' + config_get(CONFIG, "wizard_interface", "button_restart_success", "Restart", lng_key) + '","class_content":"btn-secondary","message":"' + config_get(CONFIG, "wizard_interface", "message_restart_success", "Restart?", lng_key) + '","transmit_empty":"True"}'))
            else:
                send_json["config_live"]["app_wizard_active_input_left"] = {}
                if config_getboolean(CONFIG_WIZARD, "input", "restart_success", False, lng_key):
                    send_json["config_live"]["app_wizard_active_input_left"]["0"] = build_interface_content(json.loads('{"type":"submit_confirm","name":"app_wizard_restart","tabindex":"32","content":"' + config_get(CONFIG, "wizard_interface", "button_restart_success", "Restart", lng_key) + '","class_content":"btn-secondary","message":"' + config_get(CONFIG, "wizard_interface", "message_restart_success", "Restart?", lng_key) + '","transmit_empty":"True"}'))
                if config_getboolean(CONFIG_WIZARD, "input", "abort", True, lng_key):
                    send_json["config_live"]["app_wizard_active_input_left"]["1"] = build_interface_content(json.loads('{"type":"submit_confirm","name":"app_wizard_abort","tabindex":"31","content":"' + config_get(CONFIG, "wizard_interface", "button_abort", "Abort", lng_key) + '","class_content":"btn-secondary","message":"' + config_get(CONFIG, "wizard_interface", "message_abort", "Abort?", lng_key) + '","transmit_empty":"True"}'))
                if config_getboolean(CONFIG_WIZARD, "input", "abort_group", False, lng_key):
                    send_json["config_live"]["app_wizard_active_input_left"]["2"] = build_interface_content(json.loads('{"type":"submit_confirm","name":"app_wizard_abort_group","tabindex":"30","content":"' + config_get(CONFIG, "wizard_interface", "button_abort_group", "Abort all", lng_key) + '","class_content":"btn-secondary","message":"' + config_get(CONFIG, "wizard_interface", "message_abort_group", "Abort all?", lng_key) + '","transmit_empty":"True"}'))

                if CONFIG["wizard_process"].getboolean("next"):
                    if config_get(CONFIG_WIZARD, "execute", "next", "", lng_key) != "":
                        receive_json["data"] = {}
                        receive_json["data"]["app_wizard_start"] = config_get(CONFIG_WIZARD, "execute", "next", "", lng_key)
                        process_wizard_set(receive_json, send_json)

        if process_wizard_group_input(CONFIG_WIZARD["tmp"]["execute_group"], CONFIG_WIZARD["tmp"]["execute_current"], lng_key) == "":
            if CONFIG["wizard_process"].getboolean("require_reboot_now") and CONFIG_WIZARD["tmp"]["require_reboot_now"] != "":
                output = output + "\n" + config_get(CONFIG, "wizard_interface", "output_reboot", "", lng_key)
                send_json["config_live"]["app_wizard_active_input_right"] = build_interface_content(json.loads('{"0":{"type":"submit_confirm","name":"app_wizard_reboot","tabindex":"20","autofocus":"true","content":"' + config_get(CONFIG, "wizard_interface", "button_reboot", "Reboot", lng_key) + '","class_content":"btn-success","message":"' + config_get(CONFIG, "wizard_interface", "message_reboot", "Reboot now?", lng_key) + '","transmit_empty":"True","value_view_toggle":"app_wizard_active_input,app_wizard_active_input_left,app_wizard_active_input_expert","cmd_success":"reconnect"}}'))
                send_json["config_live"]["app_wizard_active_input_left"] = ""
            else:
                process_wizard_require()
        else:
            process_wizard_require(False)

        send_json["config_live"]["app_wizard_active_input"] = ""
        send_json["config_live"]["app_wizard_active_input_expert"] = ""
        send_json["data_live"]["app_wizard_active_status"] = "footer finish"
        send_json["data_live"]["app_wizard_active_status_group"] = process_wizard_group_status(CONFIG_WIZARD["tmp"]["execute_group"], CONFIG_WIZARD["tmp"]["execute_current"])
        if CONFIG["wizard_process"].getboolean("log_state"):
            send_json["data_live"]["app_wizard_active_log"] += '\n<span class="' + config_get(CONFIG, "wizard_interface", "class_finish", "", lng_key) + '">' + config_get(CONFIG, "wizard_interface", "log_finish", "", lng_key) + "</span>"

    elif output != "":
        state = "running"
        log("State: Running", LOG_EXTREME)
        
        if config_getboolean(CONFIG_WIZARD, "input", "generate", True, lng_key):
            output = "\n" + output + "\n"

            if CONFIG["wizard_process"]["input_generate_mode"] == "replace" or input_generate == "":
                input_generate = output
            input_generate = "\n" + input_generate + "\n"

            for x in range(1):
                if CONFIG["wizard_process"].getboolean("input_generate_force") or config_getboolean(CONFIG_WIZARD, "input", "generate_force", False, lng_key):
                    send_json["config_live"]["app_wizard_active_input"] = build_interface_content(json.loads('{"0":{"type":"text","name":"app_wizard_cmd","tabindex":"10","autofocus":"true","class":"inline"}}'))
                    send_json["config_live"]["app_wizard_active_input_right"] = build_interface_content(json.loads('{"0":{"type":"submit","name":"app_wizard_cmd_btn","tabindex":"20","content":"' + config_get(CONFIG, "wizard_interface", "button_input", "Next", lng_key) + '","class_content":"btn-success","value_view_toggle":"app_wizard_active_input,app_wizard_active_input_right,app_wizard_active_input_expert"}}'))
                    send_json["data_live"]["app_wizard_active_status"] = "footer active"
                    log("Input used: Force", LOG_EXTREME)
                    state = "input"
                    break

                if CONFIG["wizard_process"].getboolean("input_generate_default") or config_getboolean(CONFIG_WIZARD, "input", "generate_default", False, lng_key):
                    if re.search(r'.*\[(\d+)\]\s?(.*)\n', input_generate):
                        array = ["="]
                        regex = re.findall(r'.*\[(\d+)\]\s?(.*)\n', output)
                        for match in regex:
                            add = match[0]+"="+match[1]
                            add.replace(";", "")
                            array.append(add)
                        string = ";".join(array)
                        send_json["config_live"]["app_wizard_active_input"] = json.loads('{"0":{"type":"select","name":"app_wizard_cmd","tabindex":"10","autofocus":"true","class":"inline"}}')
                        send_json["config_live"]["app_wizard_active_input"]["0"]["values"] = string
                        send_json["config_live"]["app_wizard_active_input"] = build_interface_content(send_json["config_live"]["app_wizard_active_input"])
                        send_json["config_live"]["app_wizard_active_input_right"] = build_interface_content(json.loads('{"0":{"type":"submit","name":"app_wizard_cmd_btn","tabindex":"20","content":"' + config_get(CONFIG, "wizard_interface", "button_input", "Next", lng_key) + '","class_content":"btn-success","value_view_toggle":"app_wizard_active_input,app_wizard_active_input_right,app_wizard_active_input_expert"}}'))
                        send_json["data_live"]["app_wizard_active_status"] = "footer active"
                        output = re.sub(r'.*\[(\d+)\]\s?(.*)\n', '', output, flags=re.M)
                        log("Input used: Select []", LOG_EXTREME)
                        state = "input"
                        break

                    if re.search(r'^(\d+)\)\s?(.*)$', input_generate, flags=re.M):
                        array = ["="]
                        regex = re.findall(r'^(\d+)\)\s?(.*)$', output, flags=re.M)
                        for match in regex:
                            add = match[0]+"="+match[1]
                            add.replace(";", "")
                            array.append(add)
                        string = ";".join(array)
                        send_json["config_live"]["app_wizard_active_input"] = json.loads('{"0":{"type":"select","name":"app_wizard_cmd","tabindex":"10","autofocus":"true","class":"inline"}}')
                        send_json["config_live"]["app_wizard_active_input"]["0"]["values"] = string
                        send_json["config_live"]["app_wizard_active_input"] = build_interface_content(send_json["config_live"]["app_wizard_active_input"])
                        send_json["config_live"]["app_wizard_active_input_right"] = build_interface_content(json.loads('{"0":{"type":"submit","name":"app_wizard_cmd_btn","tabindex":"20","content":"' + config_get(CONFIG, "wizard_interface", "button_input", "Next", lng_key) + '","class_content":"btn-success","value_view_toggle":"app_wizard_active_input,app_wizard_active_input_right,app_wizard_active_input_expert"}}'))
                        send_json["data_live"]["app_wizard_active_status"] = "footer active"
                        output = re.sub(r'^(\d+)\)\s?(.*)$', '', output, flags=re.M)
                        log("Input used: Select )", LOG_EXTREME)
                        state = "input"
                        break

                    if re.search(r'^(\d+)\.\s(.*)$', input_generate, flags=re.M):
                        array = ["="]
                        regex = re.findall(r'^(\d+)\.\s(.*)$', output, flags=re.M)
                        for match in regex:
                            add = match[0]+"="+match[1]
                            add.replace(";", "")
                            array.append(add)
                        string = ";".join(array)
                        send_json["config_live"]["app_wizard_active_input"] = json.loads('{"0":{"type":"select","name":"app_wizard_cmd","tabindex":"10","autofocus":"true","class":"inline"}}')
                        send_json["config_live"]["app_wizard_active_input"]["0"]["values"] = string
                        send_json["config_live"]["app_wizard_active_input"] = build_interface_content(send_json["config_live"]["app_wizard_active_input"])
                        send_json["config_live"]["app_wizard_active_input_right"] = build_interface_content(json.loads('{"0":{"type":"submit","name":"app_wizard_cmd_btn","tabindex":"20","content":"' + config_get(CONFIG, "wizard_interface", "button_input", "Next", lng_key) + '","class_content":"btn-success","value_view_toggle":"app_wizard_active_input,app_wizard_active_input_right,app_wizard_active_input_expert"}}'))
                        send_json["data_live"]["app_wizard_active_status"] = "footer active"
                        output = re.sub(r'^(\d+)\.\s(.*)$', '', output, flags=re.M)
                        log("Input used: Select .", LOG_EXTREME)
                        state = "input"
                        break

                    if group := re.search(r'[\[\(]([yYjJ]|yes|Yes|YES)\/([nN]|no|No|NO)[\]\)]', input_generate):
                        send_json["config_live"]["app_wizard_active_input"] = ""
                        send_json["config_live"]["app_wizard_active_input_right"] = build_interface_content(json.loads('{"0":{"type":"submit","name":"app_wizard_cmd","tabindex":"20","autofocus":"true","content":"' + config_get(CONFIG, "wizard_interface", "button_yes", "Yes", lng_key) + '","class_content":"btn-success","value":"'+group[1]+'","transmit_empty":"True","value_view_toggle":"app_wizard_active_input,app_wizard_active_input_right,app_wizard_active_input_expert"},"1":{"type":"submit","name":"app_wizard_cmd","tabindex":"21","content":"' + config_get(CONFIG, "wizard_interface", "button_no", "No", lng_key) + '","class_content":"btn-secondary","value":"'+group[2]+'","transmit_empty":"True","value_view_toggle":"app_wizard_active_input,app_wizard_active_input_right,app_wizard_active_input_expert"}}'))
                        send_json["data_live"]["app_wizard_active_status"] = "footer active"
                        output = re.sub(r'[\[\(]([yYjJ]|yes|Yes|YES)\/([nN]|no|No|NO)[\]\)]', '', output, flags=re.M)
                        log("Input used: Button yn", LOG_EXTREME)
                        state = "input"
                        break

                    if group := re.search(r'[\[\(]([yYjJ]|yes|Yes|YES)\/([nN]|no|No|NO)\/([cC]|cancel|Cancel|CANCEL)[\]\)]', input_generate):
                        send_json["config_live"]["app_wizard_active_input"] = ""
                        send_json["config_live"]["app_wizard_active_input_right"] = build_interface_content(json.loads('{"0":{"type":"submit","name":"app_wizard_cmd","tabindex":"20","autofocus":"true","content":"' + config_get(CONFIG, "wizard_interface", "button_yes", "Yes", lng_key) + '","class_content":"btn-success","value":"'+group[1]+'","transmit_empty":"True","value_view_toggle":"app_wizard_active_input,app_wizard_active_input_right,app_wizard_active_input_expert"},"1":{"type":"submit","name":"app_wizard_cmd","tabindex":"21","content":"' + config_get(CONFIG, "wizard_interface", "button_no", "No", lng_key) + '","class_content":"btn-secondary","value":"'+group[2]+'","transmit_empty":"True","value_view_toggle":"app_wizard_active_input,app_wizard_active_input_right,app_wizard_active_input_expert"},"2":{"type":"submit","name":"app_wizard_cmd","tabindex":"22","content":"' + config_get(CONFIG, "wizard_interface", "button_cancel", "Cancel", lng_key) + '","class_content":"btn-secondary","value":"'+group[3]+'","transmit_empty":"True","value_view_toggle":"app_wizard_active_input,app_wizard_active_input_right,app_wizard_active_input_expert"}}'))
                        send_json["data_live"]["app_wizard_active_status"] = "footer active"
                        output = re.sub(r'[\[\(]([yYjJ]|yes|Yes|YES)\/([nN]|no|No|NO)\/([cC]|cancel|Cancel|CANCEL)[\]\)]', '', output, flags=re.M)
                        log("Input used: Button ync", LOG_EXTREME)
                        state = "input"
                        break

                    if re.search(r'.*([Hh]it [Ee]nter|[Pp]ress [Ee]nter|[Dd]rücken[\w\s]+([Ww]eiter|[Ee]nter|[Ee]ingabetaste)).*', output) or re.search(r'.*Press Enter.*', input_generate):
                        send_json["config_live"]["app_wizard_active_input"] = ""
                        send_json["config_live"]["app_wizard_active_input_right"] = build_interface_content(json.loads('{"0":{"type":"submit","name":"app_wizard_cmd","tabindex":"20","autofocus":"true","content":"' + config_get(CONFIG, "wizard_interface", "button_enter", "Next", lng_key) + '","class_content":"btn-success","value_view_toggle":"app_wizard_active_input,app_wizard_active_input_right,app_wizard_active_input_expert","transmit_empty":"True"}}'))
                        send_json["data_live"]["app_wizard_active_status"] = "footer active"
                        log("Input used: Button enter", LOG_EXTREME)
                        state = "input"
                        break

                    if re.search(r'([Pp]assword|[Pp]asswort|[Kk]ennwort).*:', input_generate):
                        send_json["config_live"]["app_wizard_active_input"] = build_interface_content(json.loads('{"0":{"type":"passwordverify","name":"app_wizard_cmd","tabindex":"10","autofocus":"true","class":"inline"}}'))
                        send_json["config_live"]["app_wizard_active_input_right"] = build_interface_content(json.loads('{"0":{"type":"submit","name":"app_wizard_cmd_btn","tabindex":"20","content":"' + config_get(CONFIG, "wizard_interface", "button_enter", "Next", lng_key) + '","class_content":"btn-success","value_view_toggle":"app_wizard_active_input,app_wizard_active_input_right,app_wizard_active_input_expert"}}'))
                        send_json["data_live"]["app_wizard_active_status"] = "footer active"
                        log("Input used: Password", LOG_EXTREME)
                        state = "input"
                        break

                    if re.search(r'([Ee]nter.*:|.*\?.*)', input_generate):
                        send_json["config_live"]["app_wizard_active_input"] = build_interface_content(json.loads('{"0":{"type":"text","name":"app_wizard_cmd","tabindex":"10","autofocus":"true","class":"inline"}}'))
                        send_json["config_live"]["app_wizard_active_input_right"] = build_interface_content(json.loads('{"0":{"type":"submit","name":"app_wizard_cmd_btn","tabindex":"20","content":"' + config_get(CONFIG, "wizard_interface", "button_enter", "Next", lng_key) + '","class_content":"btn-success","value_view_toggle":"app_wizard_active_input,app_wizard_active_input_right,app_wizard_active_input_expert"}}'))
                        send_json["data_live"]["app_wizard_active_status"] = "footer active"
                        log("Input used: Text enter", LOG_EXTREME)
                        state = "input"
                        break

                    send_json["config_live"]["app_wizard_active_input"] = ""
                    send_json["config_live"]["app_wizard_active_input_right"] = ""
                    send_json["data_live"]["app_wizard_active_status"] = "footer running"
                    log("Input used: None", LOG_EXTREME)
                    break

            output = re.sub(r'^\n|\n$', '', output)

        send_json["config_live"]["app_wizard_active_input_left"] = {}
        if config_getboolean(CONFIG_WIZARD, "input", "abort", True, lng_key):
            send_json["config_live"]["app_wizard_active_input_left"]["0"] = build_interface_content(json.loads('{"type":"submit_confirm","name":"app_wizard_abort","tabindex":"31","content":"' + config_get(CONFIG, "wizard_interface", "button_abort", "Abort", lng_key) + '","class_content":"btn-secondary","message":"' + config_get(CONFIG, "wizard_interface", "message_abort", "Abort?", lng_key) + '","transmit_empty":"True"}'))
        if config_getboolean(CONFIG_WIZARD, "input", "abort_group", False, lng_key):
            send_json["config_live"]["app_wizard_active_input_left"]["1"] = build_interface_content(json.loads('{"type":"submit_confirm","name":"app_wizard_abort_group","tabindex":"30","content":"' + config_get(CONFIG, "wizard_interface", "button_abort_group", "Abort all", lng_key) + '","class_content":"btn-secondary","message":"' + config_get(CONFIG, "wizard_interface", "message_abort_group", "Abort all?", lng_key) + '","transmit_empty":"True"}'))

        send_json["config_live"]["app_wizard_active_input_expert"] = build_interface_content(json.loads('{"0":{"type":"textbutton","name":"app_wizard_cmd","class":"inline","content":"OK","value_view_toggle":"app_wizard_active_input,app_wizard_active_input_right,app_wizard_active_input_expert","transmit":"True"}}'))

    else:
        state = "running"

    if CONFIG["wizard_process"].getboolean("output_replace_double_lines"):
        output = re.sub(r'^(.*)(\r?\n\1)+$', r'\1', output, flags=re.M)

    if CONFIG["wizard_process"].getboolean("output_replace_unnecessary_characters"):
        output = re.sub(r'^[\-\_]+|[\-\_]+$', '', output)
        output = re.sub(r'^[^a-zA-Z0-9]$', '', output, flags=re.M)
        output = re.sub(r'^#\?$', '', output, flags=re.M)
        output = re.sub(r'^\d$', '', output, flags=re.M)
        output = re.sub(r'\?\s?:', '?', output)

    if CONFIG["wizard_process"].getboolean("output_replace_whitespace"):
        output = re.sub(r'^\s+|\s+$', '', output)
        output = re.sub(r'^ +| +$', '', output, flags=re.M)

    if CONFIG["wizard_process"].getboolean("output"):
        output_state = config_get(CONFIG_WIZARD, "output", state, "", lng_key)
        if output_state != "":
            send_json["data_live"]["app_wizard_active_output"] = output_state
        else:
            if state_append:
                process_wizard_get.output = re.sub(r'.*\n(.*)$', r'\1', getattr(process_wizard_get, 'output', "")) + output
                send_json["data_live"]["app_wizard_active_output"] = process_wizard_get.output
            else:
                process_wizard_get.output = output
                send_json["data_live"]["app_wizard_active_output"] = output
    else:
        if state_append:
            process_wizard_get.output = re.sub(r'.*\n(.*)$', r'\1', getattr(process_wizard_get, 'output', "")) + output
            send_json["data_live"]["app_wizard_active_output"] = process_wizard_get.output
        else:
            process_wizard_get.output = output
            send_json["data_live"]["app_wizard_active_output"] = output

    if not config_getboolean(CONFIG_WIZARD, "input", "output", True, lng_key):
        send_json["data_live"]["app_wizard_active_output"] = ""

    return True




def process_wizard_set(receive_json, send_json):
    global VARIABLES_SESSION
    global CONFIG_WIZARD
    global TERMINAL


    if "app_wizard_run" in receive_json["data"] and not CONFIG["wizard_process"].getboolean("group"):
        receive_json["data"]["app_wizard_start"] = receive_json["data"]["app_wizard_run"]


    if "app_wizard_run" in receive_json["data"] and CONFIG["wizard_process"].getboolean("group"):
        log("Process Wizard SET - Run", LOG_EXTREME)

        TERMINAL = None

        if "lng" not in receive_json or not CONFIG["main"].getboolean("lng_auto"):
            receive_json["lng"] = CONFIG["main"]["lng"]
        lng_key, lng_delimiter = build_lng(receive_json["lng"])

        try:
            CONFIG_WIZARD = configparser.ConfigParser(allow_no_value=True, inline_comment_prefixes="#")
            CONFIG_WIZARD.sections()
            file_handler = open(CONFIG["path"]["wizard_files"] + "/" + receive_json["data"]["app_wizard_run"] + "." + CONFIG["wizard"]["extension"])
            file_string = file_handler.read()
            file_handler.close() 
            if CONFIG["config_process"].getboolean("internal"):
                file_string = process_variable(file_string)
                file_string = process_if(file_string)
                file_string = process_cleanup(file_string)
            CONFIG_WIZARD.read_string(file_string)
        except:
            return False

        if config_get(CONFIG_WIZARD, "execute", "group", "", lng_key) == "":
            receive_json["data"]["app_wizard_start"] = receive_json["data"]["app_wizard_run"]
        else:
            if not CONFIG_WIZARD.has_section("tmp"):
                CONFIG_WIZARD.add_section("tmp")

            group_dest = []
            group_source = config_get(CONFIG_WIZARD, "execute", "group", "", lng_key)
            group_source = group_source.replace(",", ";")
            group_source = group_source.split(";")
            for x in group_source:
                x = x.strip()
                if x == "": continue
                xs = []
                if "*" in x:
                    files_source = sorted(glob.glob(CONFIG["path"]["wizard_files"] + "/" + x + "." + CONFIG["wizard"]["extension"], recursive=False))
                    for filename in files_source:
                        name = filename.replace("." + CONFIG["wizard"]["extension"], "")
                        if name.endswith(lng_key):
                            xs.append(name.rsplit("/", 1)[-1])
                        else:
                            search = name + lng_key + CONFIG["wizard"]["extension"]
                            if search not in files_source and not re.match(r'.*'+lng_delimiter+'[a-zA-Z]{2}$', name):
                                xs.append(name.rsplit("/", 1)[-1])
                else:
                    if os.path.exists(CONFIG["path"]["wizard_files"] + "/" + x + lng_key + "." + CONFIG["wizard"]["extension"]):
                        xs.append(x + lng_key)
                    elif os.path.exists(CONFIG["path"]["wizard_files"] + "/" + x + "." + CONFIG["wizard"]["extension"]):
                        xs.append(x)
                for x in xs:
                    if x == receive_json["data"]["app_wizard_run"]: continue
                    try:
                        file = configparser.ConfigParser(allow_no_value=True, inline_comment_prefixes="#")
                        file.sections()
                        file_handler = open(CONFIG["path"]["wizard_files"] + "/" + x + "." + CONFIG["wizard"]["extension"])
                        file_string = file_handler.read()
                        file_handler.close() 
                        if CONFIG["config_process"].getboolean("internal"):
                            file_string = process_variable(file_string)
                            file_string = process_if(file_string)
                            file_string = process_cleanup(file_string)
                        file.read_string(file_string)
                    except:
                        continue
                    if not file.has_option("main", "enabled_group"): continue
                    if not file["main"].getboolean("enabled_group"): continue
                    group_dest.append(x)

            CONFIG_WIZARD["tmp"]["execute"] = receive_json["data"]["app_wizard_run"]
            CONFIG_WIZARD["tmp"]["execute_group"] = ";".join(group_dest)
            CONFIG_WIZARD["tmp"]["execute_current"] = process_wizard_group(CONFIG_WIZARD["tmp"]["execute_group"])

            try:
                CONFIG_WIZARD_TMP = configparser.ConfigParser(allow_no_value=True, inline_comment_prefixes="#")
                CONFIG_WIZARD_TMP.sections()
                file_handler = open(CONFIG["path"]["wizard_files"] + "/" + CONFIG_WIZARD["tmp"]["execute_current"]  + "." + CONFIG["wizard"]["extension"])
                file_string = file_handler.read()
                file_handler.close() 
                if CONFIG["config_process"].getboolean("internal"):
                    file_string = process_variable(file_string)
                    file_string = process_if(file_string)
                    file_string = process_cleanup(file_string)
                CONFIG_WIZARD_TMP.read_string(file_string)
            except:
                return False

            process_wizard_require(False)
            if CONFIG["wizard_process"].getboolean("require_reboot_now"):
                if CONFIG_WIZARD.has_option("main", "require_reboot_now"):
                    if CONFIG_WIZARD["main"].getboolean("require_reboot_now"):
                        CONFIG_WIZARD["tmp"]["require_reboot_now"] = "True"

            send_json["data_live"]["app_wizard_active_header_icon_group"] = config_get(CONFIG_WIZARD_TMP, "main", "group_icon", "", lng_key)
            send_json["data_live"]["app_wizard_active_header_text_group"] = config_get(CONFIG_WIZARD_TMP, "main", "group", "", lng_key)
            send_json["data_live"]["app_wizard_active_header_icon_name"] = config_get(CONFIG_WIZARD_TMP, "main", "icon", "", lng_key)
            send_json["data_live"]["app_wizard_active_header_text_name"] = config_get(CONFIG_WIZARD_TMP, "main", "name", "", lng_key)
            send_json["config_live"]["app_wizard_active_input_left"] = {}
            if config_getboolean(CONFIG_WIZARD_TMP, "input", "abort", True, lng_key):
                send_json["config_live"]["app_wizard_active_input_left"]["0"] = build_interface_content(json.loads('{"type":"submit_confirm","name":"app_wizard_abort","tabindex":"31","content":"' + config_get(CONFIG, "wizard_interface", "button_abort", "Abort", lng_key) + '","class_content":"btn-secondary","message":"' + config_get(CONFIG, "wizard_interface", "message_abort", "Abort?", lng_key) + '","transmit_empty":"True"}'))
            if config_getboolean(CONFIG_WIZARD_TMP, "input", "abort_group", False, lng_key):
                send_json["config_live"]["app_wizard_active_input_left"]["1"] = build_interface_content(json.loads('{"type":"submit_confirm","name":"app_wizard_abort_group","tabindex":"30","content":"' + config_get(CONFIG, "wizard_interface", "button_abort_group", "Abort all", lng_key) + '","class_content":"btn-secondary","message":"' + config_get(CONFIG, "wizard_interface", "message_abort_group", "Abort all?", lng_key) + '","transmit_empty":"True"}'))
            if config_getboolean(CONFIG_WIZARD, "input", "skip", True, lng_key):
                input_skip = ',"1":{"type":"submit","name":"app_wizard_skip","tabindex":"21","content":"' + config_get(CONFIG, "wizard_interface", "button_skip", "Skip", lng_key) + '","class_content":"btn-secondary","value":"'+CONFIG_WIZARD["tmp"]["execute_current"]+'","transmit_empty":"True","value_view_toggle":"app_wizard_active_input,app_wizard_active_input_right,app_wizard_active_input_expert"}'
            else:
                input_skip = ''
            send_json["config_live"]["app_wizard_active_input_right"] = build_interface_content(json.loads('{"0":{"type":"submit","name":"app_wizard_start","tabindex":"20","autofocus":"true","content":"' + config_get(CONFIG, "wizard_interface", "button_start", "Start", lng_key) + '","class_content":"btn-success","value":"'+CONFIG_WIZARD["tmp"]["execute_current"]+'","transmit_empty":"True","value_view_toggle":"app_wizard_active_input,app_wizard_active_input_right,app_wizard_active_input_expert"}'+input_skip+'}'))
            send_json["config_live"]["app_wizard_active_input_expert"] = ""
            if CONFIG["wizard_process"].getboolean("output_group"):
                send_json["data_live"]["app_wizard_active_output"] = config_get(CONFIG_WIZARD_TMP, "main", "description", "", lng_key)
            elif CONFIG["wizard_process"].getboolean("output"):
                output_state = config_get(CONFIG_WIZARD_TMP, "output", "start_group", "", lng_key)
                if output_state != "":
                    send_json["data_live"]["app_wizard_active_output"] = output_state
                else:
                    send_json["data_live"]["app_wizard_active_output"] = ""
            else:
                send_json["data_live"]["app_wizard_active_output"] = ""
            send_json["data_live"]["app_wizard_active_help"] = config_get(CONFIG_WIZARD_TMP, "main", "help", "", lng_key)
            send_json["data_live"]["app_wizard_active_log"] = ""
            send_json["data_live"]["app_wizard_active_log_expert"] = ""
            send_json["data_live"]["app_wizard_active_status"] = "footer active"
            send_json["data_live"]["app_wizard_active_status_group"] = process_wizard_group_status(CONFIG_WIZARD["tmp"]["execute_group"], CONFIG_WIZARD["tmp"]["execute_current"])
            send_json["msg"] = ""


    if "app_wizard_skip" in receive_json["data"] and CONFIG["wizard_process"].getboolean("group"):
        log("Process Wizard SET - Skip", LOG_EXTREME)

        TERMINAL = None

        if "lng" not in receive_json or not CONFIG["main"].getboolean("lng_auto"):
            receive_json["lng"] = CONFIG["main"]["lng"]
        lng_key, lng_delimiter = build_lng(receive_json["lng"])

        if process_wizard_group(CONFIG_WIZARD["tmp"]["execute_group"], receive_json["data"]["app_wizard_skip"]) != "":
            receive_json["data"]["app_wizard_next"] = process_wizard_group(CONFIG_WIZARD["tmp"]["execute_group"], receive_json["data"]["app_wizard_skip"])
        else:
            send_json["config_live"]["app_wizard_active_input"] = ""
            send_json["config_live"]["app_wizard_active_input_left"] = ""
            send_json["config_live"]["app_wizard_active_input_right"] = ""
            send_json["config_live"]["app_wizard_active_input_expert"] = ""
            if CONFIG["wizard_process"].getboolean("output"):
                output_state = config_get(CONFIG_WIZARD, "output", "end_group", "", lng_key)
                if output_state != "":
                    send_json["data_live"]["app_wizard_active_output"] = output_state
                else:
                    send_json["data_live"]["app_wizard_active_output"] = ""
            else:
                send_json["data_live"]["app_wizard_active_output"] = ""
            send_json["data_live"]["app_wizard_active_status_group"] = process_wizard_group_status(CONFIG_WIZARD["tmp"]["execute_group"], receive_json["data"]["app_wizard_skip"])

            process_wizard_require()

            CONFIG_WIZARD = None


    if "app_wizard_abort" in receive_json["data"] and CONFIG["wizard_process"].getboolean("group"):
        log("Process Wizard SET - Abort (Group)", LOG_EXTREME)

        if "lng" not in receive_json or not CONFIG["main"].getboolean("lng_auto"):
            receive_json["lng"] = CONFIG["main"]["lng"]
        lng_key, lng_delimiter = build_lng(receive_json["lng"])

        if CONFIG_WIZARD["tmp"]["execute_group"] != "":
            if process_wizard_group(CONFIG_WIZARD["tmp"]["execute_group"], CONFIG_WIZARD["tmp"]["execute_current"]) != "":
                receive_json["data"]["app_wizard_next"] = process_wizard_group(CONFIG_WIZARD["tmp"]["execute_group"], CONFIG_WIZARD["tmp"]["execute_current"])
                del receive_json["data"]["app_wizard_abort"]


    if "app_wizard_next" in receive_json["data"] and CONFIG["wizard_process"].getboolean("group"):
        log("Process Wizard SET - Next", LOG_EXTREME)

        TERMINAL = None

        if "lng" not in receive_json or not CONFIG["main"].getboolean("lng_auto"):
            receive_json["lng"] = CONFIG["main"]["lng"]
        lng_key, lng_delimiter = build_lng(receive_json["lng"])

        try:
            CONFIG_WIZARD_TMP = configparser.ConfigParser(allow_no_value=True, inline_comment_prefixes="#")
            CONFIG_WIZARD_TMP.sections()
            file_handler = open(CONFIG["path"]["wizard_files"] + "/" + receive_json["data"]["app_wizard_next"] + "." + CONFIG["wizard"]["extension"])
            file_string = file_handler.read()
            file_handler.close() 
            if CONFIG["config_process"].getboolean("internal"):
                file_string = process_variable(file_string)
                file_string = process_if(file_string)
                file_string = process_cleanup(file_string)
            CONFIG_WIZARD_TMP.read_string(file_string)
        except:
            return False

        if config_getboolean(CONFIG_WIZARD_TMP, "input", "autostart", False, lng_key):
            receive_json["data"]["app_wizard_start"] = receive_json["data"]["app_wizard_next"]
        else:
            CONFIG_WIZARD["tmp"]["execute_current"] = receive_json["data"]["app_wizard_next"]

            send_json["data_live"]["app_wizard_active_header_icon_group"] = config_get(CONFIG_WIZARD_TMP, "main", "group_icon", "", lng_key)
            send_json["data_live"]["app_wizard_active_header_text_group"] = config_get(CONFIG_WIZARD_TMP, "main", "group", "", lng_key)
            send_json["data_live"]["app_wizard_active_header_icon_name"] = config_get(CONFIG_WIZARD_TMP, "main", "icon", "", lng_key)
            send_json["data_live"]["app_wizard_active_header_text_name"] = config_get(CONFIG_WIZARD_TMP, "main", "name", "", lng_key)
            send_json["config_live"]["app_wizard_active_input"] = ""
            send_json["config_live"]["app_wizard_active_input_left"] = {}
            if config_getboolean(CONFIG_WIZARD_TMP, "input", "abort", True, lng_key):
                send_json["config_live"]["app_wizard_active_input_left"]["0"] = build_interface_content(json.loads('{"type":"submit_confirm","name":"app_wizard_abort","tabindex":"31","content":"' + config_get(CONFIG, "wizard_interface", "button_abort", "Abort", lng_key) + '","class_content":"btn-secondary","message":"' + config_get(CONFIG, "wizard_interface", "message_abort", "Abort?", lng_key) + '","transmit_empty":"True"}'))
            if config_getboolean(CONFIG_WIZARD_TMP, "input", "abort_group", False, lng_key):
                send_json["config_live"]["app_wizard_active_input_left"]["1"] = build_interface_content(json.loads('{"type":"submit_confirm","name":"app_wizard_abort_group","tabindex":"30","content":"' + config_get(CONFIG, "wizard_interface", "button_abort_group", "Abort all", lng_key) + '","class_content":"btn-secondary","message":"' + config_get(CONFIG, "wizard_interface", "message_abort_group", "Abort all?", lng_key) + '","transmit_empty":"True"}'))
            if config_getboolean(CONFIG_WIZARD, "input", "skip", True, lng_key):
                input_skip = ',"1":{"type":"submit","name":"app_wizard_skip","tabindex":"21","content":"' + config_get(CONFIG, "wizard_interface", "button_skip", "Skip", lng_key) + '","class_content":"btn-secondary","value":"'+receive_json["data"]["app_wizard_next"]+'","transmit_empty":"True","value_view_toggle":"app_wizard_active_input,app_wizard_active_input_right,app_wizard_active_input_expert"}'
            else:
                input_skip = ''
            send_json["config_live"]["app_wizard_active_input_right"] = build_interface_content(json.loads('{"0":{"type":"submit","name":"app_wizard_start","tabindex":"20","autofocus":"true","content":"' + config_get(CONFIG, "wizard_interface", "button_start", "Start", lng_key) + '","class_content":"btn-success","value":"'+receive_json["data"]["app_wizard_next"]+'","transmit_empty":"True","value_view_toggle":"app_wizard_active_input,app_wizard_active_input_right,app_wizard_active_input_expert"}'+input_skip+'}'))
            send_json["config_live"]["app_wizard_active_input_expert"] = ""
            if CONFIG["wizard_process"].getboolean("output_group"):
                send_json["data_live"]["app_wizard_active_output"] = config_get(CONFIG_WIZARD_TMP, "main", "description", "", lng_key)
            elif CONFIG["wizard_process"].getboolean("output"):
                output_state = config_get(CONFIG_WIZARD_TMP, "output", "start_group", "", lng_key)
                if output_state != "":
                    send_json["data_live"]["app_wizard_active_output"] = output_state
                else:
                    send_json["data_live"]["app_wizard_active_output"] = ""
            else:
                send_json["data_live"]["app_wizard_active_output"] = ""
            send_json["data_live"]["app_wizard_active_help"] = config_get(CONFIG_WIZARD_TMP, "main", "help", "", lng_key)
            send_json["data_live"]["app_wizard_active_log"] = ""
            send_json["data_live"]["app_wizard_active_log_expert"] = ""
            send_json["data_live"]["app_wizard_active_status"] = "footer active"
            send_json["data_live"]["app_wizard_active_status_group"] = process_wizard_group_status(CONFIG_WIZARD["tmp"]["execute_group"], receive_json["data"]["app_wizard_next"])
            send_json["msg"] = ""


    if "app_wizard_restart" in receive_json["data"]:
        log("Process Wizard SET - Restart", LOG_EXTREME)
        if CONFIG_WIZARD.has_section("tmp"):
            if CONFIG_WIZARD.has_option("tmp", "execute_current"):
                receive_json["data"]["app_wizard_start"] = CONFIG_WIZARD["tmp"]["execute_current"]


    if "app_wizard_start" in receive_json["data"]:
        log("Process Wizard SET - Start", LOG_EXTREME)

        TERMINAL = None

        if "lng" not in receive_json or not CONFIG["main"].getboolean("lng_auto"):
            receive_json["lng"] = CONFIG["main"]["lng"]
        lng_key, lng_delimiter = build_lng(receive_json["lng"])

        execute = config_get(CONFIG_WIZARD, "tmp", "execute", "", lng_key)
        execute_group = config_get(CONFIG_WIZARD, "tmp", "execute_group", "", lng_key)
        require_acknowledge = config_get(CONFIG_WIZARD, "tmp", "require_acknowledge", "", lng_key)
        require_reboot = config_get(CONFIG_WIZARD, "tmp", "require_reboot", "", lng_key)
        require_reboot_now = config_get(CONFIG_WIZARD, "tmp", "require_reboot_now", "", lng_key)
        require_reload = config_get(CONFIG_WIZARD, "tmp", "require_reload", "", lng_key)

        try:
            CONFIG_WIZARD = configparser.ConfigParser(allow_no_value=True, inline_comment_prefixes="#")
            CONFIG_WIZARD.sections()
            file_handler = open(CONFIG["path"]["wizard_files"] + "/" + receive_json["data"]["app_wizard_start"] + "." + CONFIG["wizard"]["extension"])
            file_string = file_handler.read()
            file_handler.close() 
            if CONFIG["config_process"].getboolean("internal"):
                file_string = process_variable(file_string)
                file_string = process_if(file_string)
                file_string = process_cleanup(file_string)
            CONFIG_WIZARD.read_string(file_string)
        except:
            return False

        if not CONFIG_WIZARD.has_section("tmp"):
            CONFIG_WIZARD.add_section("tmp")

        CONFIG_WIZARD["tmp"]["execute"] = execute
        CONFIG_WIZARD["tmp"]["execute_group"] = execute_group
        CONFIG_WIZARD["tmp"]["require_acknowledge"] = require_acknowledge
        CONFIG_WIZARD["tmp"]["require_reboot"] = require_reboot
        CONFIG_WIZARD["tmp"]["require_reboot_now"] = require_reboot_now
        CONFIG_WIZARD["tmp"]["require_reload"] = require_reload
        CONFIG_WIZARD["tmp"]["execute_current"] = receive_json["data"]["app_wizard_start"]

        if CONFIG["wizard_process"].getboolean("system_load"):
             net_io = psutil.net_io_counters()
             process_wizard_get.net_time = time.time()
             process_wizard_get.net_bytes_recv = net_io.bytes_recv
             process_wizard_get.net_bytes_sent = net_io.bytes_sent
        process_wizard_get.output = ""

        if CONFIG["wizard_process"].getboolean("output_replace_lng"):
            files = []
            file = CONFIG["path"]["wizard_files"] + "/" + receive_json["data"]["app_wizard_start"] + lng_key + "." + CONFIG["wizard"]["extension_lng"]
            if os.path.isfile(file):
                files.append(file)
            else:
                file = CONFIG["path"]["wizard_files"] + "/" + receive_json["data"]["app_wizard_start"] + "." + CONFIG["wizard"]["extension_lng"]
                if os.path.isfile(file):
                    files.append(file)
            section = "files_lng"
            if CONFIG_WIZARD.has_section(section+lng_key):
                for (key, val) in CONFIG_WIZARD.items(section+lng_key):
                    file = CONFIG["path"]["wizard_files"] + "/" + key + lng_key + "." + CONFIG["wizard"]["extension_lng"]
                    if os.path.isfile(file):
                        files.append(file)
                    else:
                        file = CONFIG["path"]["wizard_files"] + "/" + key + "." + CONFIG["wizard"]["extension_lng"]
                        if os.path.isfile(file):
                            files.append(file)
            elif CONFIG_WIZARD.has_section(section):
                for (key, val) in CONFIG_WIZARD.items(section):
                    file = CONFIG["path"]["wizard_files"] + "/" + key + lng_key + "." + CONFIG["wizard"]["extension_lng"]
                    if os.path.isfile(file):
                        files.append(file)
                    else:
                        file = CONFIG["path"]["wizard_files"] + "/" + key + "." + CONFIG["wizard"]["extension_lng"]
                        if os.path.isfile(file):
                            files.append(file)
            if len(files) > 0:
                if not CONFIG_WIZARD.has_section("tmp_files_lng"):
                    CONFIG_WIZARD.add_section("tmp_files_lng")
                index = 0
                for file in files:
                    CONFIG_WIZARD["tmp_files_lng"][str(index)] = file
                    index += 1

        send_json["data_live"]["app_wizard_active_header_icon_group"] = config_get(CONFIG_WIZARD, "main", "group_icon", "", lng_key)
        send_json["data_live"]["app_wizard_active_header_text_group"] = config_get(CONFIG_WIZARD, "main", "group", "", lng_key)
        send_json["data_live"]["app_wizard_active_header_icon_name"] = config_get(CONFIG_WIZARD, "main", "icon", "", lng_key)
        send_json["data_live"]["app_wizard_active_header_text_name"] = config_get(CONFIG_WIZARD, "main", "name", "", lng_key)
        send_json["config_live"]["app_wizard_active_input"] = ""
        send_json["config_live"]["app_wizard_active_input_left"] = ""
        send_json["config_live"]["app_wizard_active_input_right"] = ""
        send_json["config_live"]["app_wizard_active_input_expert"] = ""
        if CONFIG["wizard_process"].getboolean("output"):
            output_state = config_get(CONFIG_WIZARD, "output", "start", "", lng_key)
            if output_state != "":
                send_json["data_live"]["app_wizard_active_output"] = output_state
            else:
                send_json["data_live"]["app_wizard_active_output"] = ""
        else:
            send_json["data_live"]["app_wizard_active_output"] = ""
        send_json["data_live"]["app_wizard_active_help"] = config_get(CONFIG_WIZARD, "main", "help", "", lng_key)
        send_json["data_live"]["app_wizard_active_log"] = ""
        send_json["data_live"]["app_wizard_active_log_expert"] = ""
        send_json["data_live"]["app_wizard_active_status"] = "footer running"
        send_json["data_live"]["app_wizard_active_status_group"] = process_wizard_group_status(CONFIG_WIZARD["tmp"]["execute_group"], CONFIG_WIZARD["tmp"]["execute_current"])
        send_json["msg"] = ""

        cmd = ""
        cmd_execute = ""
        if CONFIG["wizard_process"].getboolean("script") and cmd == "":
            cmd = config_get(CONFIG_WIZARD, "execute", "script", "", lng_key)
            if cmd != "" and not cmd.startswith("/"):
                cmd_execute = "cd " + CONFIG["path"]["wizard_templates"] + " && ./" + cmd
        if CONFIG["wizard_process"].getboolean("cmd") and cmd == "":
            cmd = config_get(CONFIG_WIZARD, "execute", "cmd", "", lng_key)
        if CONFIG["wizard_process"].getboolean("fallback") and cmd == "":
            if os.path.isfile(CONFIG["path"]["wizard_templates"] + "/" + receive_json["data"]["app_wizard_start"] + "." + CONFIG["wizard"]["extension_template"]):
                cmd = receive_json["data"]["app_wizard_start"] + "." + CONFIG["wizard"]["extension_template"]
                cmd_execute = "cd " + CONFIG["path"]["wizard_templates"] + " && ./" + cmd
        if cmd_execute == "":
            cmd_execute = cmd

        CONFIG_WIZARD["tmp"]["log"] = ""
        CONFIG_WIZARD["tmp"]["log_time"] = ""
        CONFIG_WIZARD["tmp"]["cmd"] = cmd_execute
        if CONFIG["wizard_process"].getboolean("log_input_initial"):
            CONFIG_WIZARD["tmp"]["cmd_log"] = cmd
        else:
            CONFIG_WIZARD["tmp"]["cmd_log"] = ""

        if cmd_execute != "":
            log("Starting wizard terminal session", LOG_EXTREME)
            log("CMD: " + cmd_execute, LOG_EXTREME)
            if CONFIG.has_option("path", "terminal"):
                path = CONFIG["path"]["terminal"]
            else:
                path = ""
            cmd = config_get(CONFIG, "wizard_process", "terminal_cmd", "bash", lng_key)
            cmd_args = config_get(CONFIG, "wizard_process", "terminal_cmd_args", "", lng_key)
            env_str = config_get(CONFIG, "wizard_process", "terminal_env", "", lng_key)
            env = None
            if env_str != "":
                env = defaultdict(dict)
                env_array = env_str.split(";")
                for x in env_array:
                    x = x.strip()
                    y = x.split("=")
                    if len(y) == 2:
                      env[y[0].strip()] = y[1].strip()
            timeout = config_getint(CONFIG, "wizard_process", "terminal_timeout", 100, lng_key)
            read_bytes = config_getint(CONFIG, "wizard_process", "terminal_read_bytes", 20, lng_key)
            rows = config_getint(CONFIG, "wizard_process", "terminal_size_rows", 100, lng_key)
            cols = config_getint(CONFIG, "wizard_process", "terminal_size_cols", 200, lng_key)
            restart_session = config_getboolean(CONFIG, "wizard_process", "terminal_restart_session", True, lng_key)
            TERMINAL = terminal_class(path, cmd, cmd_args, env, timeout, read_bytes, rows, cols, restart_session)
            TERMINAL.set(cmd_execute)
        else:
            log("Building wizard config interface", LOG_EXTREME)
            #todo: build config interface

            if CONFIG["wizard_process"].getboolean("output"):
                output_state = config_get(CONFIG_WIZARD, "output", "error", "", lng_key)
                if output_state != "":
                    send_json["data_live"]["app_wizard_active_output"] = output_state
                else:
                    send_json["data_live"]["app_wizard_active_output"] = ""
            send_json["data_live"]["app_wizard_active_status"] = "footer abort"
            if CONFIG["wizard_process"].getboolean("log_state"):
                send_json["data_live"]["app_wizard_active_log"] = '\n<span class="' + config_get(CONFIG, "wizard_interface", "class_error", "", lng_key) + '">' + config_get(CONFIG, "wizard_interface", "log_error", "", lng_key) + "</span>"
            return False


    if "app_wizard_cmd" in receive_json["data"]:
        log("Process Wizard SET - CMD", LOG_EXTREME)

        if "lng" not in receive_json or not CONFIG["main"].getboolean("lng_auto"):
            receive_json["lng"] = CONFIG["main"]["lng"]
        lng_key, lng_delimiter = build_lng(receive_json["lng"])

        send_json["data_live"]["app_wizard_active_status"] = "footer running"
        input = receive_json["data"]["app_wizard_cmd"]
        if CONFIG["wizard_process"].getboolean("input_replace_whitespace"):
            input = input.replace("\r\r", "\n")
            input = input.replace("\r", "")
            input = re.sub(r'^\s+|\s+$', '', input)

        section = "input_replace"
        if CONFIG["wizard_process"].getboolean(section):
            if CONFIG_WIZARD.has_section(section+lng_key):
                section = section+lng_key
                for (key_search, val_search) in CONFIG_WIZARD.items(section):
                    if key_search.endswith("search"):
                        key_replace = key_search.replace("search", "replace")
                        if CONFIG_WIZARD.has_option(section, key_replace):
                            input = input.replace(val_search, CONFIG_WIZARD[section][key_replace])
            elif CONFIG_WIZARD.has_section(section):
                for (key_search, val_search) in CONFIG_WIZARD.items(section):
                    if key_search.endswith("search"):
                        key_replace = key_search.replace("search", "replace")
                        if CONFIG_WIZARD.has_option(section, key_replace):
                            input = input.replace(val_search, CONFIG_WIZARD[section][key_replace])

        section = "input_regex"
        if CONFIG["wizard_process"].getboolean(section):
            if CONFIG_WIZARD.has_section(section+lng_key):
                section = section+lng_key
                for (key_search, val_search) in CONFIG_WIZARD.items(section):
                    if key_search.endswith("search"):
                        key_replace = key_search.replace("search", "replace")
                        if CONFIG_WIZARD.has_option(section, key_replace):
                            input = re.sub(val_search, CONFIG_WIZARD[section][key_replace], input)
            elif CONFIG_WIZARD.has_section(section):
                for (key_search, val_search) in CONFIG_WIZARD.items(section):
                    if key_search.endswith("search"):
                        key_replace = key_search.replace("search", "replace")
                        if CONFIG_WIZARD.has_option(section, key_replace):
                            input = re.sub(val_search, CONFIG_WIZARD[section][key_replace], input)

        CONFIG_WIZARD["tmp"]["cmd"] = input
        if input == "":
            CONFIG_WIZARD["tmp"]["cmd_log"] = config_get(CONFIG, "wizard_interface", "log_enter", "", lng_key)
        else:
            CONFIG_WIZARD["tmp"]["cmd_log"] = input
        log("CMD: " + input, LOG_EXTREME)
        if TERMINAL:
            TERMINAL.set(input)


    if "app_wizard_abort" in receive_json["data"] or "app_wizard_abort_group" in receive_json["data"]:
        log("Process Wizard SET - Abort", LOG_EXTREME)

        if "lng" not in receive_json or not CONFIG["main"].getboolean("lng_auto"):
            receive_json["lng"] = CONFIG["main"]["lng"]
        lng_key, lng_delimiter = build_lng(receive_json["lng"])

        send_json["config_live"]["app_wizard_active_input"] = ""
        send_json["config_live"]["app_wizard_active_input_left"] = {}
        if config_getboolean(CONFIG_WIZARD, "input", "restart_abort", False, lng_key):
            send_json["config_live"]["app_wizard_active_input_left"]["0"] = build_interface_content(json.loads('{"type":"submit_confirm","name":"app_wizard_restart","tabindex":"32","content":"' + config_get(CONFIG, "wizard_interface", "button_restart_abort", "Restart", lng_key) + '","class_content":"btn-secondary","message":"' + config_get(CONFIG, "wizard_interface", "message_restart_abort", "Restart?", lng_key) + '","transmit_empty":"True"}'))
        send_json["config_live"]["app_wizard_active_input_right"] = ""
        send_json["config_live"]["app_wizard_active_input_expert"] = ""
        if CONFIG["wizard_process"].getboolean("output"):
            output_state = config_get(CONFIG_WIZARD, "output", "abort", "", lng_key)
            if output_state != "":
                send_json["data_live"]["app_wizard_active_output"] = output_state
            else:
                send_json["data_live"]["app_wizard_active_output"] = ""
        else:
            send_json["data_live"]["app_wizard_active_output"] = ""
        send_json["data_live"]["app_wizard_active_status"] = "footer abort"
        send_json["data_live"]["app_wizard_active_status_group"] = ""
        if CONFIG["wizard_process"].getboolean("log_state"):
            send_json["data_live"]["app_wizard_active_log"] = '\n<span class="' + config_get(CONFIG, "wizard_interface", "class_abort", "", lng_key) + '">' + config_get(CONFIG, "wizard_interface", "log_abort", "", lng_key) + "</span>"

        TERMINAL = None
        CONFIG_WIZARD = None


    if "app_wizard_log_delete" in receive_json["data"]:
        log("Process Wizard SET - Log Delete", LOG_EXTREME)
        send_json["data_live"]["app_wizard_active_log"] = ""


    if "app_wizard_log_expert_delete" in receive_json["data"]:
        log("Process Wizard SET - Log Expert Delete", LOG_EXTREME)
        send_json["data_live"]["app_wizard_active_log_expert"] = ""


    if "app_wizard_reboot" in receive_json["data"]:
        log("Process Wizard SET - Reboot", LOG_EXTREME)

        VARIABLES_SESSION.pop("require_reboot", None)
        VARIABLES_SESSION.pop("require_reload", None)
        if CONFIG["wizard_process"].getboolean("group"):
            if process_wizard_group(CONFIG_WIZARD["tmp"]["execute_group"], CONFIG_WIZARD["tmp"]["execute_current"]) != "":
                VARIABLES_SESSION["wizard_execute"] = CONFIG_WIZARD["tmp"]["execute"]
                VARIABLES_SESSION["wizard_execute_current"] = process_wizard_group(CONFIG_WIZARD["tmp"]["execute_group"], CONFIG_WIZARD["tmp"]["execute_current"])
            else:
                VARIABLES_SESSION.pop("wizard_execute", None)
                VARIABLES_SESSION.pop("wizard_execute_current", None)

        try:
            with open(CONFIG["path"]["config"] + "/session_current." + CONFIG["config"]["extension"], "w") as outfile:
                json.dump(VARIABLES_SESSION, outfile)
            VARIABLES_SESSION.pop("wizard_execute", None)
            VARIABLES_SESSION.pop("wizard_execute_current", None)
        except:
            VARIABLES_SESSION.pop("wizard_execute", None)
            VARIABLES_SESSION.pop("wizard_execute_current", None)
            return False

        os.system(CONFIG["wizard_process"]["cmd_reboot"])


    return True




def process_wizard_require(execute=True):
    if CONFIG["wizard_process"].getboolean("require_acknowledge"):
        if CONFIG_WIZARD.has_option("main", "require_acknowledge"):
            if CONFIG_WIZARD["main"].getboolean("require_acknowledge"):
                CONFIG_WIZARD["tmp"]["require_acknowledge"] = "True"
        if execute and CONFIG_WIZARD["tmp"]["require_acknowledge"] != "":
            VARIABLES_SESSION["require_acknowledge"] = True

    if CONFIG["wizard_process"].getboolean("require_reboot"):
        if CONFIG_WIZARD.has_option("main", "require_reboot"):
            if CONFIG_WIZARD["main"].getboolean("require_reboot"):
                CONFIG_WIZARD["tmp"]["require_reboot"] = "True"
        if execute and CONFIG_WIZARD["tmp"]["require_reboot"] != "":
            VARIABLES_SESSION["require_reboot"] = True

    if CONFIG["wizard_process"].getboolean("require_reload"):
        if CONFIG_WIZARD.has_option("main", "require_reload"):
            if CONFIG_WIZARD["main"].getboolean("require_reload"):
                CONFIG_WIZARD["tmp"]["require_reload"] = "True"
        if execute and CONFIG_WIZARD["tmp"]["require_reload"] != "":
            VARIABLES_SESSION["require_reload"] = True




def process_wizard_group(group, current="", lng_key=""):
    if group == "":
        return ""

    ret = ""

    if current == "":
        found = True
    else:
        found = False

    group = group.replace(",", ";")
    group = group.split(";")
    for x in group:
        x = x.strip()
        if found:
            ret = x
            break
        if x == current:
            found = True

    return ret




def process_wizard_group_status(group, current, lng_key=""):
    if group == "" or current == "":
        return ""

    ret = ""

    found = False

    group = group.replace(",", ";")
    group = group.split(";")
    for x in group:
        x = x.strip()
        if x == current:
            found = True
            ret = ret + "<span class='wizard_status active'></span>"
        elif found == False:
            ret = ret + "<span class='wizard_status active'></span>"
        else:
            ret = ret + "<span class='wizard_status'></span>"
    return ret




def process_wizard_group_input(group, current, lng_key=""):
    if group == "" or current == "":
        return ""

    ret = ""

    found = False

    group = group.replace(",", ";")
    group = group.split(";")
    for x in group:
        x = x.strip()
        if found:
            ret = x
            break
        if x == current:
            found = True

    if ret != "":
        ret = build_interface_content(json.loads('{"0":{"type":"submit","name":"app_wizard_next","tabindex":"20","autofocus":"true","content":"' + config_get(CONFIG, "wizard_interface", "button_next", "Next", lng_key) + '","class_content":"btn-success","value":"'+ret+'","transmit_empty":"True","value_view_toggle":"app_wizard_active_input,app_wizard_active_input_right,app_wizard_active_input_expert"}}'))

    return ret


##############################################################################################################
# Process require


def process_require(config):
    if config != "":
        if re.match(r'([^\s(]+)(\s+)?(==|!=)(\s+)?[\'\"]?([^\s\'\")]+)[\'\"]?', config):
            config = re.sub(r' && ', r' and ', config)
            config = re.sub(r' \|\| ', r' or ', config)
            config = re.sub(r'([^\s(]+)(\s+)?(==|!=)(\s+)?[\'\"]?([^\s\'\")]+)[\'\"]?', r'VARIABLES["\1"] \3 "\5"', config)
            print(config)
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
                    if x in VARIABLES: return False
                else:
                    if x not in VARIABLES: return False
    return True




def process_require_mode(config):
    global VARIABLES_SESSION

    if config != "":
        config = config.lower()
        config = config.replace(" ", ";")
        config = config.replace(",", ";")
        config = config.split(";")
        for x in config:
            x = x.strip()
            if x.startswith("!"):
                x = x[1:]
                if x != VARIABLES_SESSION["mode"]: return False
            else:
                if x == VARIABLES_SESSION["mode"]: return True
        return False

    return True


##############################################################################################################
# Execute


def execute(config, data):
    if config == "": return False
    config = config.replace(",", ";")
    config = config.split(";")
    for x in config:
        x = x.strip()
        if x == "any" or x == "all" or x in data: return True
    return False




def execute_file(source, destination, file=None, type="text", permission=None, owner=None):
    if type == "log" or type == "log_file" or type == "log_cmd":
        return True

    if CONFIG["main"].getboolean("mode_test"):
        destination = CONFIG["path"]["mode_test"] + destination

    log("Execute file: " + source + " -> " + destination, LOG_DEBUG)

    if file == None:
        file = os.path.basename(source)

    if not os.path.exists(os.path.dirname(destination)) and not CONFIG["config_process"].getboolean("files_create_path"):
        return False

    if not os.path.exists(os.path.dirname(destination)) and CONFIG["config_process"].getboolean("files_create_path"):
        Path(os.path.dirname(destination)).mkdir(parents=True, exist_ok=True)
        log("Path created: " + os.path.dirname(destination), LOG_DEBUG)

    if not os.path.exists(destination) and not CONFIG["config_process"].getboolean("files_create_file"):
        return False

    if type == "auto":
        if not execute_file_text(source, destination): return False
    elif type == "env":
        if not execute_file_env(source, destination, file): return False
    elif type == "env_edit":
        if not execute_file_env_edit(source, destination, file): return False
    elif type == "ini":
        if not execute_file_ini(source, destination, file): return False
    elif type == "ini_edit":
        if not execute_file_ini_edit(source, destination, file): return False
    elif type == "json":
        if not execute_file_json(source, destination, file): return False
    elif type == "json_edit":
        if not execute_file_json_edit(source, destination, file): return False
    elif type == "keyarg":
        if not execute_file_keyarg(source, destination, file): return False
    elif type == "keyarg_edit":
        if not execute_file_keyarg_edit(source, destination, file): return False
    elif type == "keyval":
        if not execute_file_keyval(source, destination, file): return False
    elif type == "keyval_edit":
        if not execute_file_keyval_edit(source, destination, file): return False
    elif type == "raw":
        if not execute_file_raw(source, destination, file): return False
    elif type == "raw_edit":
        if not execute_file_raw_edit(source, destination, file): return False
    elif type == "text":
        if not execute_file_text(source, destination): return False
    elif type == "toml":
        if not execute_file_toml(source, destination, file): return False
    elif type == "toml_edit":
        if not execute_file_toml_edit(source, destination, file): return False
    elif type == "xml":
        if not execute_file_xml(source, destination, file): return False
    elif type == "xml_edit":
        if not execute_file_xml_edit(source, destination, file): return False
    elif type == "yaml":
        if not execute_file_yaml(source, destination, file): return False
    elif type == "yaml_edit":
        if not execute_file_yaml_edit(source, destination, file): return False
    else:
        return False

    if CONFIG["config_process"].getboolean("files_permission") and permission:
        os.chmod(destination, int(permission, 8))
        log("Permission changed to: " + permission, LOG_DEBUG)

    if CONFIG["config_process"].getboolean("files_owner") and owner:
        owner = owner.split(":")
        if len(owner) == 2:
            shutil.chown(destination, owner[0], owner[1])
            log("Owner changed to: " + owner[0] + ":" + owner[1], LOG_DEBUG)
        else:
            return False

    return True




def execute_file_env(source, destination, file=None):
    if not CONFIG["config_process"].getboolean("env_write"): return True

    if file == None: file = os.path.basename(source)

    try:
        source_file = open(source, "r")
        text = source_file.read()
        source_file.close()
    except:
        return False

    raw_keys = []

    for key in VARIABLES.keys():
        if isinstance(CONFIG_VARIABLES[key]["file"], str) and isinstance(CONFIG_VARIABLES[key]["file_section"], str):
            if CONFIG_VARIABLES[key]["file"] != "" and CONFIG_VARIABLES[key]["file_section"] != "":
                if CONFIG_VARIABLES[key]["file"] == file:
                    value = VARIABLES[key]
                    if " " in value: value = '"' + value + '"'
                    if group := re.search(r'^('+CONFIG_VARIABLES[key]["file_section"]+')=(.*)', text, flags=re.M):
                        text = re.sub(r'^('+CONFIG_VARIABLES[key]["file_section"]+')=(.*)', r'\1='+value, text, flags=re.M)
                    elif group := re.search(r'^#('+CONFIG_VARIABLES[key]["file_section"]+')=(.*)', text, flags=re.M):
                        text = re.sub(r'^#('+CONFIG_VARIABLES[key]["file_section"]+')=(.*)', r'\1='+value, text, flags=re.M)
                    elif CONFIG["config_process"].getboolean("env_add"):
                        text = text + "\n" + CONFIG_VARIABLES[key]["file_section"] + "=" + value
        elif isinstance(CONFIG_VARIABLES[key]["file"], str):
            if CONFIG_VARIABLES[key]["file"] != "" and CONFIG_VARIABLES[key]["file"] == file:
                raw_keys.append(key)

    if len(raw_keys) > 0 and CONFIG["config_process"].getboolean("env_raw") and CONFIG.has_option("config", "delimiter_variable_raw"):
        if CONFIG["config"]["delimiter_variable_raw"] != "":
            text_search = "\n" + text + "\n"
            for key in raw_keys:
                if isinstance(VARIABLES_DATA[key], str):
                    text_replace = CONFIG["config"]["delimiter_variable_raw"] + key + CONFIG["config"]["delimiter_variable_raw"] + "\n" + VARIABLES_DATA[key].replace("\\n", "\n") + "\n" + CONFIG["config"]["delimiter_variable_raw"]
                    if regex := re.findall(r'[^'+CONFIG["config"]["delimiter_variable_raw"][0]+']('+CONFIG["config"]["delimiter_variable_raw"]+'('+key+')'+CONFIG["config"]["delimiter_variable_raw"]+'((\n|.)*?)'+CONFIG["config"]["delimiter_variable_raw"]+')[^'+CONFIG["config"]["delimiter_variable_raw"][0]+']', text_search):
                        for match in regex:
                            text = text.replace(match[0], text_replace)
                    else:
                        text = text + "\n" + text_replace

    try:
        destination_file = open(destination, "w+")
        destination_file.write(text)
        destination_file.close()
    except:
        return False

    return True




def execute_file_env_edit(source, destination, file=None):
    if not CONFIG["config_process"].getboolean("env_write"): return True

    if file == None: file = os.path.basename(source)

    if os.path.exists(destination): source = destination

    return execute_file_env(source, destination, file)




def execute_file_ini(source, destination, file=None):
    if not CONFIG["config_process"].getboolean("ini_write"): return True

    if file == None: file = os.path.basename(source)

    try:
        config = ConfigObj(source, file_error=True, write_empty_values=True, encoding="utf8")
    except:
        return False

    raw_keys = []

    for key in VARIABLES.keys():
        if isinstance(CONFIG_VARIABLES[key]["file"], str) and isinstance(CONFIG_VARIABLES[key]["file_section"], str) and isinstance(CONFIG_VARIABLES[key]["file_key"], str):
            if CONFIG_VARIABLES[key]["file"] != "" and CONFIG_VARIABLES[key]["file_section"] != "" and CONFIG_VARIABLES[key]["file_key"] != "":
                if CONFIG_VARIABLES[key]["file"] == file:
                    if isinstance(CONFIG_VARIABLES[key]["file_subkey"], str):
                        if CONFIG_VARIABLES[key]["file_subkey"] != "":
                            if CONFIG_VARIABLES[key]["file_section"] in config and CONFIG_VARIABLES[key]["file_key"] in config[CONFIG_VARIABLES[key]["file_section"]] and CONFIG_VARIABLES[key]["file_subkey"] in config[CONFIG_VARIABLES[key]["file_section"]][CONFIG_VARIABLES[key]["file_key"]]:
                                if isinstance(config[CONFIG_VARIABLES[key]["file_section"]][CONFIG_VARIABLES[key]["file_key"]][CONFIG_VARIABLES[key]["file_subkey"]], str):
                                    config[CONFIG_VARIABLES[key]["file_section"]][CONFIG_VARIABLES[key]["file_key"]][CONFIG_VARIABLES[key]["file_subkey"]] = VARIABLES[key]
                            elif CONFIG["config_process"].getboolean("ini_add"):
                                config[CONFIG_VARIABLES[key]["file_section"]][CONFIG_VARIABLES[key]["file_key"]][CONFIG_VARIABLES[key]["file_subkey"]] = VARIABLES[key]
                        else:
                            if CONFIG_VARIABLES[key]["file_section"] in config and CONFIG_VARIABLES[key]["file_key"] in config[CONFIG_VARIABLES[key]["file_section"]]:
                                if isinstance(config[CONFIG_VARIABLES[key]["file_section"]][CONFIG_VARIABLES[key]["file_key"]], str):
                                    config[CONFIG_VARIABLES[key]["file_section"]][CONFIG_VARIABLES[key]["file_key"]] = VARIABLES[key]
                            elif CONFIG["config_process"].getboolean("ini_add"):
                                config[CONFIG_VARIABLES[key]["file_section"]][CONFIG_VARIABLES[key]["file_key"]] = VARIABLES[key]
                    else:
                        if CONFIG_VARIABLES[key]["file_section"] in config and CONFIG_VARIABLES[key]["file_key"] in config[CONFIG_VARIABLES[key]["file_section"]]:
                            if isinstance(config[CONFIG_VARIABLES[key]["file_section"]][CONFIG_VARIABLES[key]["file_key"]], str):
                                config[CONFIG_VARIABLES[key]["file_section"]][CONFIG_VARIABLES[key]["file_key"]] = VARIABLES[key]
                        elif CONFIG["config_process"].getboolean("ini_add"):
                            config[CONFIG_VARIABLES[key]["file_section"]][CONFIG_VARIABLES[key]["file_key"]] = VARIABLES[key]
        elif isinstance(CONFIG_VARIABLES[key]["file"], str):
            if CONFIG_VARIABLES[key]["file"] != "" and CONFIG_VARIABLES[key]["file"] == file:
                raw_keys.append(key)

    config.filename = destination
    config.write()

    if len(raw_keys) > 0 and CONFIG["config_process"].getboolean("ini_raw") and CONFIG.has_option("config", "delimiter_variable_raw"):
        if CONFIG["config"]["delimiter_variable_raw"] != "":
            try:
                with open(destination, 'r+') as file:
                    text = file.read()
                    text_search = "\n" + text + "\n"
                    for key in raw_keys:
                        if isinstance(VARIABLES_DATA[key], str):
                            text_replace = CONFIG["config"]["delimiter_variable_raw"] + key + CONFIG["config"]["delimiter_variable_raw"] + "\n" + VARIABLES_DATA[key].replace("\\n", "\n") + "\n" + CONFIG["config"]["delimiter_variable_raw"]
                            if regex := re.findall(r'[^'+CONFIG["config"]["delimiter_variable_raw"][0]+']('+CONFIG["config"]["delimiter_variable_raw"]+'('+key+')'+CONFIG["config"]["delimiter_variable_raw"]+'((\n|.)*?)'+CONFIG["config"]["delimiter_variable_raw"]+')[^'+CONFIG["config"]["delimiter_variable_raw"][0]+']', text_search):
                                for match in regex:
                                    text = text.replace(match[0], text_replace)
                            else:
                                text = text + "\n" + text_replace
                    file.seek(0)
                    file.write(text)
                    file.truncate()
            except:
                return False

    return True




def execute_file_ini_edit(source, destination, file=None):
    if not CONFIG["config_process"].getboolean("ini_write"): return True

    if file == None: file = os.path.basename(source)

    if os.path.exists(destination): source = destination

    return execute_file_ini(source, destination, file)




def execute_file_json(source, destination, file=None):
    if not CONFIG["config_process"].getboolean("json_write"): return True

    if file == None: file = os.path.basename(source)
    #todo
    return True




def execute_file_json_edit(source, destination, file=None):
    if not CONFIG["config_process"].getboolean("json_write"): return True

    if file == None: file = os.path.basename(source)

    if os.path.exists(destination): source = destination

    return execute_file_json(source, destination, file)




def execute_file_keyarg(source, destination, file=None):
    if not CONFIG["config_process"].getboolean("keyarg_write"): return True

    if file == None: file = os.path.basename(source)

    try:
        source_file = open(source, "r")
        text = source_file.read()
        source_file.close()
    except:
        return False

    raw_keys = []

    for key in VARIABLES.keys():
        if isinstance(CONFIG_VARIABLES[key]["file"], str) and isinstance(CONFIG_VARIABLES[key]["file_section"], str):
            if CONFIG_VARIABLES[key]["file"] != "" and CONFIG_VARIABLES[key]["file_section"] != "":
                if CONFIG_VARIABLES[key]["file"] == file:
                    value = VARIABLES[key]
                    if " " in value: value = '"' + value + '"'
                    if group := re.search(r'^((\s+)?'+CONFIG_VARIABLES[key]["file_section"]+')\s(.*)', text, flags=re.M):
                        text = re.sub(r'^((\s+)?'+CONFIG_VARIABLES[key]["file_section"]+')\s(.*)', r'\1 '+value, text, flags=re.M)
                    elif group := re.search(r'^#((\s+)?'+CONFIG_VARIABLES[key]["file_section"]+')\s(.*)', text, flags=re.M):
                        text = re.sub(r'^#((\s+)?'+CONFIG_VARIABLES[key]["file_section"]+')\s(.*)', r'\1 '+value, text, flags=re.M)
                    elif CONFIG["config_process"].getboolean("keyarg_add"):
                        text = text + "\n" + CONFIG_VARIABLES[key]["file_section"] + " " + value
        elif isinstance(CONFIG_VARIABLES[key]["file"], str):
            if CONFIG_VARIABLES[key]["file"] != "" and CONFIG_VARIABLES[key]["file"] == file:
                raw_keys.append(key)

    if len(raw_keys) > 0 and CONFIG["config_process"].getboolean("keyarg_raw") and CONFIG.has_option("config", "delimiter_variable_raw"):
        if CONFIG["config"]["delimiter_variable_raw"] != "":
            text_search = "\n" + text + "\n"
            for key in raw_keys:
                if isinstance(VARIABLES_DATA[key], str):
                    text_replace = CONFIG["config"]["delimiter_variable_raw"] + key + CONFIG["config"]["delimiter_variable_raw"] + "\n" + VARIABLES_DATA[key].replace("\\n", "\n") + "\n" + CONFIG["config"]["delimiter_variable_raw"]
                    if regex := re.findall(r'[^'+CONFIG["config"]["delimiter_variable_raw"][0]+']('+CONFIG["config"]["delimiter_variable_raw"]+'('+key+')'+CONFIG["config"]["delimiter_variable_raw"]+'((\n|.)*?)'+CONFIG["config"]["delimiter_variable_raw"]+')[^'+CONFIG["config"]["delimiter_variable_raw"][0]+']', text_search):
                        for match in regex:
                            text = text.replace(match[0], text_replace)
                    else:
                        text = text + "\n" + text_replace

    try:
        destination_file = open(destination, "w+")
        destination_file.write(text)
        destination_file.close()
    except:
        return False

    return True




def execute_file_keyarg_edit(source, destination, file=None):
    if not CONFIG["config_process"].getboolean("keyarg_write"): return True

    if file == None: file = os.path.basename(source)

    if os.path.exists(destination): source = destination

    return execute_file_keyarg(source, destination, file)




def execute_file_keyval(source, destination, file=None):
    if not CONFIG["config_process"].getboolean("keyval_write"): return True

    if file == None: file = os.path.basename(source)

    try:
        source_file = open(source, "r")
        text = source_file.read()
        source_file.close()
    except:
        return False

    raw_keys = []

    for key in VARIABLES.keys():
        if isinstance(CONFIG_VARIABLES[key]["file"], str) and isinstance(CONFIG_VARIABLES[key]["file_section"], str):
            if CONFIG_VARIABLES[key]["file"] != "" and CONFIG_VARIABLES[key]["file_section"] != "":
                if CONFIG_VARIABLES[key]["file"] == file:
                    value = VARIABLES[key]
                    if group := re.search(r'^((\s+)?'+CONFIG_VARIABLES[key]["file_section"]+')(\s+)?=(\s+)?(.*)', text, flags=re.M):
                        text = re.sub(r'^((\s+)?'+CONFIG_VARIABLES[key]["file_section"]+')(\s+)?=(\s+)?(.*)', r'\1='+value, text, flags=re.M)
                    elif group := re.search(r'^#((\s+)?'+CONFIG_VARIABLES[key]["file_section"]+')(\s+)?=(\s+)?(.*)', text, flags=re.M):
                        text = re.sub(r'^#((\s+)?'+CONFIG_VARIABLES[key]["file_section"]+')(\s+)?=(\s+)?(.*)', r'\1='+value, text, flags=re.M)
                    elif CONFIG["config_process"].getboolean("keyval_add"):
                        text = text + "\n" + CONFIG_VARIABLES[key]["file_section"] + "=" + value
        elif isinstance(CONFIG_VARIABLES[key]["file"], str):
            if CONFIG_VARIABLES[key]["file"] != "" and CONFIG_VARIABLES[key]["file"] == file:
                raw_keys.append(key)

    if len(raw_keys) > 0 and CONFIG["config_process"].getboolean("keyval_raw") and CONFIG.has_option("config", "delimiter_variable_raw"):
        if CONFIG["config"]["delimiter_variable_raw"] != "":
            text_search = "\n" + text + "\n"
            for key in raw_keys:
                if isinstance(VARIABLES_DATA[key], str):
                    text_replace = CONFIG["config"]["delimiter_variable_raw"] + key + CONFIG["config"]["delimiter_variable_raw"] + "\n" + VARIABLES_DATA[key].replace("\\n", "\n") + "\n" + CONFIG["config"]["delimiter_variable_raw"]
                    if regex := re.findall(r'[^'+CONFIG["config"]["delimiter_variable_raw"][0]+']('+CONFIG["config"]["delimiter_variable_raw"]+'('+key+')'+CONFIG["config"]["delimiter_variable_raw"]+'((\n|.)*?)'+CONFIG["config"]["delimiter_variable_raw"]+')[^'+CONFIG["config"]["delimiter_variable_raw"][0]+']', text_search):
                        for match in regex:
                            text = text.replace(match[0], text_replace)
                    else:
                        text = text + "\n" + text_replace

    try:
        destination_file = open(destination, "w+")
        destination_file.write(text)
        destination_file.close()
    except:
        return False

    return True




def execute_file_keyval_edit(source, destination, file=None):
    if not CONFIG["config_process"].getboolean("keyval_write"): return True

    if file == None: file = os.path.basename(source)

    if os.path.exists(destination): source = destination

    return execute_file_keyval(source, destination, file)




def execute_file_raw(source, destination, file=None):
    if not CONFIG["config_process"].getboolean("raw_write"): return True

    if file == None: file = os.path.basename(source)

    for key in VARIABLES.keys():
        if isinstance(CONFIG_VARIABLES[key]["file"], str):
            if CONFIG_VARIABLES[key]["file"] != "" and CONFIG_VARIABLES[key]["file"] == file:
                try:
                    destination_file = open(destination, "w+")
                    destination_file.write(VARIABLES[key])
                    destination_file.close()
                except:
                    return False
    return True




def execute_file_raw_edit(source, destination, file=None):
    if not CONFIG["config_process"].getboolean("raw_write"): return True

    if file == None: file = os.path.basename(source)

    if os.path.exists(destination): source = destination

    return execute_file_raw(source, destination, file)




def execute_file_text(source, destination):
    if not CONFIG["config_process"].getboolean("text_write"): return True

    try:
        source_file = open(source, "r")
        text = source_file.read()
        source_file.close()
    except:
        return False

    text = process_variable(text)
    text = process_if(text)
    text = process_cleanup(text)

    try:
        destination_file = open(destination, "w+")
        destination_file.write(text)
        destination_file.close()
    except:
        return False

    return True




def execute_file_toml(source, destination, file=None):
    if not CONFIG["config_process"].getboolean("toml_write"): return True

    if file == None: file = os.path.basename(source)
    #todo
    return True




def execute_file_toml_edit(source, destination, file=None):
    if not CONFIG["config_process"].getboolean("toml_write"): return True

    if file == None: file = os.path.basename(source)

    if os.path.exists(destination): source = destination

    return execute_file_toml(source, destination, file)




def execute_file_xml(source, destination, file=None):
    if not CONFIG["config_process"].getboolean("xml_write"): return True

    if file == None: file = os.path.basename(source)
    #todo
    return True




def execute_file_xml_edit(source, destination, file=None):
    if not CONFIG["config_process"].getboolean("xml_write"): return True

    if file == None: file = os.path.basename(source)

    if os.path.exists(destination): source = destination

    return execute_file_xml(source, destination, file)




def execute_file_yaml(source, destination, file=None):
    if not CONFIG["config_process"].getboolean("yaml_write"): return True

    if file == None: file = os.path.basename(source)
    #todo
    return True




def execute_file_yaml_edit(source, destination, file=None):
    if not CONFIG["config_process"].getboolean("yaml_write"): return True

    if file == None: file = os.path.basename(source)

    if os.path.exists(destination): source = destination

    return execute_file_yaml(source, destination, file)




def execute_cmd(cmd):
    if CONFIG["main"].getboolean("mode_test"):
        log("Execute cmd: " + cmd, LOG_DEBUG)
        log("Execute cmd: " + cmd, LOG_FORCE, CONFIG["path"]["mode_test"] + "/log.log")
    else:
        log("Execute cmd: " + cmd, LOG_DEBUG)
        try:
            result = subprocess.run(cmd, capture_output=True, shell=True, text=True)
            log(result.returncode, LOG_DEBUG)
            log(result.stdout + result.stderr, LOG_DEBUG)
            if result.returncode != 0: return False
        except:
            return False
    return True




def execute_script(script):
    if CONFIG["main"].getboolean("mode_test"):
        log("Execute script: " + script, LOG_DEBUG)
        log("Execute script: " + script, LOG_FORCE, CONFIG["path"]["mode_test"] + "/log.log")
    else:
        log("Execute script: " + script, LOG_DEBUG)
        try:
            result = subprocess.run(script, capture_output=True, shell=True, text=True)
            log(result.returncode, LOG_DEBUG)
            log(result.stdout + result.stderr, LOG_DEBUG)
            if result.returncode != 0: return False
        except:
            return False
    return True


##############################################################################################################
# Build


def build(option="setup", lng=""):
    log("**** Build ****", LOG_DEBUG)

    error = []

    if not CONFIG.has_section("build"):
        error.append("build - " + option)
        return error

    if not CONFIG.has_option("build", option):
        error.append("build - " + option)
        return error

    option = CONFIG["build"][option]
    option = option.lower()
    option = option.replace(" ", ";")
    option = option.replace(",", ";")
    option = option.split(";")
    for x in option:
        x = x.strip()

        if x == "variables_system":
            if CONFIG["config_process"].getboolean("variables_system"):
                if not VARIABLES_SYSTEM.build(): error.append("variables_system - build")
                log("VARIABLES_SYSTEM", LOG_DEBUG)
                log(VARIABLES_SYSTEM.data, LOG_DEBUG)

        if x == "variables_system_add":
            if CONFIG["config_process"].getboolean("variables_system") and CONFIG.has_option("build_add", "system"):
                if not VARIABLES_SYSTEM.add(CONFIG, CONFIG["build_add"]["system"]): error.append("variables_system - add")
                if not VARIABLES_SYSTEM.add(VARIABLES_SOFTWARE["package_raw"], "software_package_raw"): error.append("variables_system - add")
                if not VARIABLES_SYSTEM.add(VARIABLES_SOFTWARE["python_raw"], "software_python_raw"): error.append("variables_system - add")
                if not VARIABLES_SYSTEM.add(VARIABLES_SOFTWARE["software_raw"], "software_software_raw"): error.append("variables_system - add")

        if x == "variables_user":
            if CONFIG["config_process"].getboolean("variables_user"):
                if not VARIABLES_USER.build(): error.append("variables_user - build")
                log("VARIABLES_USER", LOG_DEBUG)
                log(VARIABLES_USER.data, LOG_DEBUG)

        if x == "variables_user_add":
            if CONFIG["config_process"].getboolean("variables_user") and CONFIG.has_option("build_add", "user"):
                if not VARIABLES_USER.add(CONFIG, CONFIG["build_add"]["user"]): error.append("variables_user - add")

        if x == "merge":
            if not process_variable_merge(): error.append("process_variable_merge")

        if x == "software":
            error_current = build_software(lng)
            if len(error_current ) > 0:
                error.append("build_software")
                error = error + error_current

        if x == "interface":
            error_current = build_interface(lng)
            if len(error_current ) > 0:
                error.append("build_interface")
                error = error + error_current

        if x == "config":
            error_current = build_config(lng)
            if len(error_current ) > 0:
                error.append("build_config")
                error = error + error_current

        if x == "data":
            error_current = build_data(lng)
            if len(error_current ) > 0:
                error.append("build_data")
                error = error + error_current

        if x == "data_read":
            if not data_read(): error.append("data_read")

        if x == "data_read_file":
            if not data_read_file(): error.append("data_read_file")

    if len(error) > 0:
        log("Build: " + ", ".join(error), LOG_ERROR)

    return error




def build_variables_regex(text):
    if CONFIG["config_process"].getboolean("variables_regex"):
        if CONFIG["config_process"]["variables_regex_search"] != "":
            text = re.sub(CONFIG["config_process"]["variables_regex_search"], CONFIG["config_process"]["variables_regex_replace"], text)
    return text




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




def build_files(path, extension, lng_key="", recursive=False):
    if path == "" or extension == "":
        return []
    extension = "." + extension

    if lng_key == "":
        return sorted(glob.glob(path + "/*" + extension, recursive=recursive))

    lng_key, lng_delimiter = build_lng(lng_key)

    files = []
    files_source = sorted(glob.glob(path + "/*" + extension, recursive=recursive))
    for filename in files_source:
        name = filename.replace(extension, "")
        if name.endswith(lng_key):
            files.append(filename)
        else:
            search = name + lng_key + extension
            if search not in files_source and not re.match(r'.*'+lng_delimiter+'[a-zA-Z]{2}$', name):
                files.append(filename)
    return files


##############################################################################################################
# Build interface


def build_interface(lng=""):
    global CONFIG_VARIABLES_INTERFACE
    global CONFIG_INTERFACE

    CONFIG_VARIABLES_INTERFACE = defaultdict(dict)

    error = []

    config_page = defaultdict(lambda : defaultdict(dict))
    config_tab = defaultdict(lambda : defaultdict(lambda : defaultdict(dict)))
    config_content = defaultdict(lambda : defaultdict(lambda : defaultdict(lambda : defaultdict(dict))))

    config_system_sections = CONFIG["config"]["system_sections"].split(";")

    lng_key, lng_delimiter = build_lng(lng)

    files = build_files(CONFIG["path"]["config_files"], CONFIG["config"]["extension"], lng)
    for filename in files:
        try:
            file_name = os.path.basename(filename)
            file = configparser.ConfigParser(allow_no_value=True, inline_comment_prefixes="#")
            file.sections()
            file_handler = open(filename)
            file_string = file_handler.read()
            file_handler.close()
            if CONFIG["config_process"].getboolean("internal"):
                file_string = process_variable(file_string)
                file_string = process_if(file_string)
                file_string = process_cleanup(file_string)
            file.read_string(file_string)
        except:
            error.append("Error in file: " + file_name)
            continue

        if not file.has_option("main", "enabled"): continue
        if not file["main"].getboolean("enabled"): continue

        if file.has_option("main", "require") and CONFIG["config_process"].getboolean("require"):
            if not process_require(file["main"]["require"]): continue

        if file.has_option("main", "require_mode") and CONFIG["config_process"].getboolean("require_mode"):
            if not process_require_mode(file["main"]["require_mode"]): continue

        if file.has_option("main", "require_software") and CONFIG["config_process"].getboolean("require_software") and CONFIG["software"].getboolean("enabled"):
            if not process_software_require(file["main"]["require_software"]): continue

        if file.has_option("main", "require_system") and CONFIG["config_process"].getboolean("require_system"):
            if not VARIABLES_SYSTEM.require(file["main"]["require_system"]): continue

        if file.has_option("main", "require_user") and CONFIG["config_process"].getboolean("require_user"):
            if not VARIABLES_SYSTEM.require(file["main"]["require_user"]): continue

        if file.has_option("main", "type"):
            match = False
            if not match:
                if file["main"]["type"] == "content":
                    match = True
                    if not CONFIG["interface_process"].getboolean("content"):
                        continue

            if not match:
                if file["main"]["type"] == "config":
                    match = True
                    if not CONFIG["interface_process"].getboolean("config") or not CONFIG["config"].getboolean("enabled"):
                        continue

            if not match:
                if file["main"]["type"] == "software":
                    match = True
                    if not CONFIG["interface_process"].getboolean("software") or not CONFIG["software"].getboolean("enabled"):
                        continue
                    else:
                        file = build_interface_software(file, lng_key)

            if not match:
                if file["main"]["type"] == "wizard" and not match:
                    match = True
                    if not CONFIG["interface_process"].getboolean("wizard") or not CONFIG["wizard"].getboolean("enabled"):
                        continue
                    else:
                        file = build_interface_wizard(file, lng_key)

        for section in file.sections():
            if file.has_section("global") and section not in config_system_sections:
                for (key, val) in file.items("global"):
                    file[section][key] = val

            if file.has_option(section, "enabled"):
                if not file[section].getboolean("enabled"):
                    continue

            if file.has_option(section, "require") and CONFIG["config_process"].getboolean("require"):
                if not process_require(file[section]["require"]): continue

            if file.has_option(section, "require_mode") and CONFIG["config_process"].getboolean("require_mode"):
                if not process_require_mode(file[section]["require_mode"]): continue

            if file.has_option(section, "require_software") and CONFIG["config_process"].getboolean("require_software") and CONFIG["software"].getboolean("enabled"):
                if not process_software_require(file[section]["require_software"]): continue

            if file.has_option(section, "require_system") and CONFIG["config_process"].getboolean("require_system"):
                if not VARIABLES_SYSTEM.require(file[section]["require_system"]): continue

            if file.has_option(section, "require_user") and CONFIG["config_process"].getboolean("require_user"):
                if not VARIABLES_USER.require(file[section]["require_user"]): continue

            section_key = build_variables_regex(section)
            if section_key in config_system_sections:
                continue

            if file.has_option(section, "page") and not file.has_option(section, "tab"):
                if group := re.match(r'(.*)(\s+)?[\\](\s+)?(.*)', file[section]["page"]):
                    file[section]["page"] = group.group(1)
                    file[section]["tab"] = group.group(4)
                else:
                    file[section]["tab"] = "footer"

            if file.has_option(section, "page"+lng_key) and not file.has_option(section, "tab"+lng_key):
                if group := re.match(r'(.*)(\s+)?[\\](\s+)?(.*)', file[section]["page"+lng_key]):
                    file[section]["page"+lng_key] = group.group(1)
                    file[section]["tab"+lng_key] = group.group(4)
                else:
                    file[section]["tab"+lng_key] = "footer"

            page_key = config_get(file, section, "page", "", lng_key)
            tab_key = config_get(file, section, "tab", "", lng_key)

            if page_key != "" and tab_key != "" and file.has_option(section, "type"):
                if file.has_option(section, "type"):
                    for (key, val) in CONFIG.items("interface_mapping_type"):
                        if file[section]["type"] == key:
                            file[section]["type"] = val

                sections = build_sections(file, section)
                if sections:
                    if not isinstance(sections, bool):
                        for sections_key in sections:
                            section_key = build_variables_regex(section + "_" + sections_key)

                            for (key, val) in CONFIG.items("interface_mapping"):
                                config_content[page_key][tab_key][section_key][key] = config_get(file, section, key, "", lng_key)

                            if file.has_option(section, "label"+lng_key):
                                config_content[page_key][tab_key][section_key]["label"] = file[section]["label"+lng_key]
                            elif file.has_option(section, "label"):
                                config_content[page_key][tab_key][section_key]["label"] = file[section]["label"]
                            elif file.has_option(section, "name"+lng_key) and CONFIG.has_option("interface_types_label", file[section]["type"]):
                                config_content[page_key][tab_key][section_key]["label"] = file[section]["name"+lng_key]
                            elif file.has_option(section, "name") and CONFIG.has_option("interface_types_label", file[section]["type"]):
                                config_content[page_key][tab_key][section_key]["label"] = file[section]["name"]
                            else:
                                config_content[page_key][tab_key][section_key]["label"] = ""

                            config_content[page_key][tab_key][section_key]["name"] = ""
                            config_content[page_key][tab_key][section_key]["value_name"] = ""
                            if file.has_option(section, "name"+lng_key) and not CONFIG["interface_process"].getboolean("name_section"):
                                config_content[page_key][tab_key][section_key]["name"] = file[section]["name"+lng_key]
                            elif file.has_option(section, "name") and not CONFIG["interface_process"].getboolean("name_section"):
                                config_content[page_key][tab_key][section_key]["name"] = file[section]["name"]
                            elif file.has_option(section, "value_name"+lng_key):
                                config_content[page_key][tab_key][section_key]["name"] = file[section]["value_name"+lng_key]
                            elif file.has_option(section, "value_name"):
                                config_content[page_key][tab_key][section_key]["name"] = file[section]["value_name"]
                            elif CONFIG.has_option("interface_types_name", file[section]["type"]):
                                config_content[page_key][tab_key][section_key]["name"] = section_key

                            if config_content[page_key][tab_key][section_key]["name"] != "":
                                CONFIG_VARIABLES_INTERFACE[config_content[page_key][tab_key][section_key]["name"]] = ""

                            config_content[page_key][tab_key][section_key]["data"] = ""
                            config_content[page_key][tab_key][section_key]["value_data"] = ""
                            if file.has_option(section, "data"+lng_key) and not CONFIG["interface_process"].getboolean("data_section"):
                                config_content[page_key][tab_key][section_key]["data"] = file[section]["data"+lng_key]
                            elif file.has_option(section, "data") and not CONFIG["interface_process"].getboolean("data_section"):
                                config_content[page_key][tab_key][section_key]["data"] = file[section]["data"]
                            elif file.has_option(section, "value_data"+lng_key):
                                config_content[page_key][tab_key][section_key]["data"] = file[section]["value_data"+lng_key]
                            elif file.has_option(section, "value_data"):
                                config_content[page_key][tab_key][section_key]["data"] = file[section]["value_data"]
                            elif CONFIG.has_option("interface_types_data", file[section]["type"]):
                                config_content[page_key][tab_key][section_key]["data"] = section_key

                            if config_content[page_key][tab_key][section_key]["data"] != "":
                                CONFIG_VARIABLES_INTERFACE[config_content[page_key][tab_key][section_key]["data"]] = ""

                            for (key, val) in CONFIG.items("interface_mapping_tab"):
                                if file.has_option(section, key+lng_key):
                                    config_tab[page_key][tab_key][val] = file[section][key+lng_key]
                                elif file.has_option(section, key):
                                    config_tab[page_key][tab_key][val] = file[section][key]
                                if "*" in key:
                                    search = key.replace("*", "")
                                    for (key, val) in file.items(section):
                                        if key.startswith(search):
                                            key = key.replace(search, "")
                                            config_tab[page_key][tab_key][key] = val

                            if file.has_option(section, "tab_label"+lng_key):
                                config_tab[page_key][tab_key]["label"] = file[section]["tab_label"+lng_key]
                            elif file.has_option(section, "tab_label"):
                                config_tab[page_key][tab_key]["label"] = file[section]["tab_label"]
                            elif file.has_option(section, "tab"+lng_key):
                                config_tab[page_key][tab_key]["label"] = file[section]["tab_label"] = file[section]["tab"+lng_key]
                            else:
                                config_tab[page_key][tab_key]["label"] = file[section]["tab_label"] = file[section]["tab"]

                            for key in config_content[page_key][tab_key][section_key].keys():
                                config_content[page_key][tab_key][section_key][key] = config_content[page_key][tab_key][section_key][key].replace(CONFIG["config"]["delimiter_sections"], sections_key)

                else:
                    for (key, val) in CONFIG.items("interface_mapping"):
                        config_content[page_key][tab_key][section_key][key] = config_get(file, section, key, "", lng_key)

                    if file.has_option(section, "label"+lng_key):
                        config_content[page_key][tab_key][section_key]["label"] = file[section]["label"+lng_key]
                    elif file.has_option(section, "label"):
                        config_content[page_key][tab_key][section_key]["label"] = file[section]["label"]
                    elif file.has_option(section, "name"+lng_key) and CONFIG.has_option("interface_types_label", file[section]["type"]):
                        config_content[page_key][tab_key][section_key]["label"] = file[section]["name"+lng_key]
                    elif file.has_option(section, "name") and CONFIG.has_option("interface_types_label", file[section]["type"]):
                        config_content[page_key][tab_key][section_key]["label"] = file[section]["name"]
                    else:
                        config_content[page_key][tab_key][section_key]["label"] = ""

                    config_content[page_key][tab_key][section_key]["name"] = ""
                    config_content[page_key][tab_key][section_key]["value_name"] = ""
                    if file.has_option(section, "name"+lng_key) and not CONFIG["interface_process"].getboolean("name_section"):
                        config_content[page_key][tab_key][section_key]["name"] = file[section]["name"+lng_key]
                    elif file.has_option(section, "name") and not CONFIG["interface_process"].getboolean("name_section"):
                        config_content[page_key][tab_key][section_key]["name"] = file[section]["name"]
                    elif file.has_option(section, "value_name"+lng_key):
                        config_content[page_key][tab_key][section_key]["name"] = file[section]["value_name"+lng_key]
                    elif file.has_option(section, "value_name"):
                        config_content[page_key][tab_key][section_key]["name"] = file[section]["value_name"]
                    elif CONFIG.has_option("interface_types_name", file[section]["type"]):
                        config_content[page_key][tab_key][section_key]["name"] = section_key

                    if config_content[page_key][tab_key][section_key]["name"] != "":
                        CONFIG_VARIABLES_INTERFACE[config_content[page_key][tab_key][section_key]["name"]] = ""

                    config_content[page_key][tab_key][section_key]["data"] = ""
                    config_content[page_key][tab_key][section_key]["value_data"] = ""
                    if file.has_option(section, "data"+lng_key) and not CONFIG["interface_process"].getboolean("data_section"):
                        config_content[page_key][tab_key][section_key]["data"] = file[section]["data"+lng_key]
                    elif file.has_option(section, "data") and not CONFIG["interface_process"].getboolean("data_section"):
                        config_content[page_key][tab_key][section_key]["data"] = file[section]["data"]
                    elif file.has_option(section, "value_data"+lng_key):
                        config_content[page_key][tab_key][section_key]["data"] = file[section]["value_data"+lng_key]
                    elif file.has_option(section, "value_data"):
                        config_content[page_key][tab_key][section_key]["data"] = file[section]["value_data"]
                    elif CONFIG.has_option("interface_types_data", file[section]["type"]):
                        config_content[page_key][tab_key][section_key]["data"] = section_key

                    if config_content[page_key][tab_key][section_key]["data"] != "":
                        CONFIG_VARIABLES_INTERFACE[config_content[page_key][tab_key][section_key]["data"]] = ""

                    for (key, val) in CONFIG.items("interface_mapping_tab"):
                        if file.has_option(section, key+lng_key):
                            config_tab[page_key][tab_key][val] = file[section][key+lng_key]
                        elif file.has_option(section, key):
                            config_tab[page_key][tab_key][val] = file[section][key]
                        if "*" in key:
                            search = key.replace("*", "")
                            for (key, val) in file.items(section):
                                if key.startswith(search):
                                    config_tab[page_key][tab_key][key.replace(search, "")] = config_get(file, section, key, "", lng_key)

                    if file.has_option(section, "tab_label"+lng_key):
                        config_tab[page_key][tab_key]["label"] = file[section]["tab_label"+lng_key]
                    elif file.has_option(section, "tab_label"):
                        config_tab[page_key][tab_key]["label"] = file[section]["tab_label"]
                    elif file.has_option(section, "tab"+lng_key):
                        config_tab[page_key][tab_key]["label"] = file[section]["tab_label"] = file[section]["tab"+lng_key]
                    else:
                        config_tab[page_key][tab_key]["label"] = file[section]["tab_label"] = file[section]["tab"]

            else:
                for (key, val) in CONFIG.items("interface_mapping"):
                    config_content[page_key][tab_key][section_key][key] = ""

            if page_key != "":
                if file.has_option(section, "page_type"):
                    config_page[page_key]["type"] = file[section]["page_type"]
                    for (key, val) in CONFIG.items("interface_mapping_type"):
                        if file[section]["page_type"] == key:
                            config_page[page_key]["type"] = val
                elif not isinstance(config_page[page_key]["type"], str):
                    config_page[page_key]["type"] = "page"

                for (key, val) in CONFIG.items("interface_mapping_page"):
                    if file.has_option(section, key+lng_key):
                        config_page[page_key][val] = file[section][key+lng_key]
                    elif file.has_option(section, key):
                        config_page[page_key][val] = file[section][key]
                    if "*" in key:
                        search = key.replace("*", "")
                        for (key, val) in file.items(section):
                            if key.startswith(search):
                                config_page[page_key][key.replace(search, "")] = config_get(file, section, key, "", lng_key)

                if file.has_option(section, "page_label"+lng_key):
                    config_page[page_key]["label"] = file[section]["page_label"+lng_key]
                elif file.has_option(section, "page_label"):
                    config_page[page_key]["label"] = file[section]["page_label"]
                elif file.has_option(section, "page"+lng_key):
                    config_page[page_key]["label"] = file[section]["page"+lng_key]
                else:
                    config_page[page_key]["label"] = file[section]["page"]

    config_interface = defaultdict(lambda : defaultdict(lambda : defaultdict(lambda : defaultdict(lambda : defaultdict(lambda : defaultdict(lambda : defaultdict(dict)))))))

    mapping_main = "main"
    if CONFIG.has_option("interface_mapping", "main"):
        mapping_main = CONFIG["interface_mapping"]["main"]

    mapping_content = "c"
    if CONFIG.has_option("interface_mapping", "content"):
        mapping_content = CONFIG["interface_mapping"]["content"]

    mapping_type = "t"
    if CONFIG.has_option("interface_mapping", "type"):
        mapping_type = CONFIG["interface_mapping"]["type"]

    mapping_name = "n"
    if CONFIG.has_option("interface_mapping", "name"):
        mapping_name = CONFIG["interface_mapping"]["name"]

    page_key = 0
    for page in config_content.keys():
        for (key, val) in CONFIG.items("interface_mapping"):
            if isinstance(config_page[page][key], str):
                if config_page[page][key] != "":
                    config_interface[mapping_content][page_key][val] = config_page[page][key]

        if page not in CONFIG["interface_mapping_page_name"]:
            tab_key = 0
            for tab in config_content[page].keys():
                if tab not in CONFIG["interface_mapping_tab_name"]:
                        for (key, val) in CONFIG.items("interface_mapping"):
                            if isinstance(config_tab[page][tab][key], str):
                                if config_tab[page][tab][key] != "":
                                    config_interface[mapping_content][page_key][mapping_content][tab_key][val] = config_tab[page][tab][key]

                        content_key = 0
                        for content in config_content[page][tab].keys():
                            if config_interface[mapping_content][page_key][mapping_type] != "page":
                                for (key, val) in CONFIG.items("interface_mapping"):
                                    if config_content[page][tab][content][key] != "":
                                        config_interface[mapping_content][page_key][val] = config_content[page][tab][content][key]
                                config_interface[mapping_content][page_key][mapping_name] = content
                            else:
                                for (key, val) in CONFIG.items("interface_mapping"):
                                    if config_content[page][tab][content][key] != "":
                                        config_interface[mapping_content][page_key][mapping_content][tab_key][mapping_content][content_key][val] = config_content[page][tab][content][key]
                                content_key = content_key + 1
                        tab_key = tab_key + 1
                else:
                    content_key = 0
                    for content in config_content[page][tab].keys():
                        for (key, val) in CONFIG.items("interface_mapping"):
                            if config_content[page][tab][content][key] != "":
                                config_interface[mapping_content][page_key][CONFIG["interface_mapping_tab_name"][tab]][content_key][val] = config_content[page][tab][content][key]
                        content_key = content_key + 1
            page_key = page_key + 1
        else:
            content_key = 0
            for tab in config_content[page].keys():
                for content in config_content[page][tab].keys():
                    for (key, val) in CONFIG.items("interface_mapping"):
                        if config_content[page][tab][content][key] != "":
                            config_interface[CONFIG["interface_mapping_page_name"][page]][content_key][val] = config_content[page][tab][content][key]
                    config_interface[CONFIG["interface_mapping_page_name"][page]][content_key][mapping_name] = content
                    content_key = content_key + 1

    for (key, val) in CONFIG.items("interface_main"):
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

    if CONFIG.has_option("interface_mapping", "default_values"):
        for (key, val) in CONFIG.items("interface_default_values"):
            if val != "":
                if lng_delimiter != "" and lng_delimiter in key:
                    if lng_key in key:
                        config_interface[CONFIG["interface_mapping"]["default_values"]][key.replace(lng_key, "")] = val
                else:                
                    config_interface[CONFIG["interface_mapping"]["default_values"]][key] = val

    if CONFIG.has_option("interface_mapping", "default_icons"):
        for (key, val) in CONFIG.items("interface_default_icons"):
            if val != "":
                if lng_delimiter != "" and lng_delimiter in key:
                    if lng_key in key:
                        config_interface[CONFIG["interface_mapping"]["default_icons"]][key.replace(lng_key, "")] = val
                else:                
                    config_interface[CONFIG["interface_mapping"]["default_icons"]][key] = val

    if CONFIG.has_option("interface_mapping", "default_messages"):
        for (key, val) in CONFIG.items("interface_default_messages"):
            if val != "":
                if lng_delimiter != "" and lng_delimiter in key:
                    if lng_key in key:
                        config_interface[CONFIG["interface_mapping"]["default_messages"]][key.replace(lng_key, "")] = val
                else:                
                    config_interface[CONFIG["interface_mapping"]["default_messages"]][key] = val

    if CONFIG.has_option("interface_mapping", "default_caption_required"):
        for (key, val) in CONFIG.items("interface_default_caption_required"):
            if val != "":
                if lng_delimiter != "" and lng_delimiter in key:
                    if lng_key in key:
                        config_interface[CONFIG["interface_mapping"]["default_caption_required"]][key.replace(lng_key, "")] = val
                else:                
                    config_interface[CONFIG["interface_mapping"]["default_caption_required"]][key] = val

    if CONFIG.has_option("interface_mapping", "default_caption_pattern"):
        for (key, val) in CONFIG.items("interface_default_caption_pattern"):
            if val != "":
                if lng_delimiter != "" and lng_delimiter in key:
                    if lng_key in key:
                        config_interface[CONFIG["interface_mapping"]["default_caption_pattern"]][key.replace(lng_key, "")] = val
                else:                
                    config_interface[CONFIG["interface_mapping"]["default_caption_pattern"]][key] = val

    CONFIG_INTERFACE = json.dumps(config_interface)

    return error




def build_interface_software(source, lng_key=""):
    error = []

    dest = configparser.ConfigParser(allow_no_value=True, inline_comment_prefixes="#")
    dest.sections()

    group = None

    page = ""
    for section in source.sections():
        page = config_get(source, section, "page", "", lng_key)
        if page != "":
            if matches := re.match(r'(.*)(\s+)?[\\](\s+)?(.*)', page):
                page = matches.group(1)
            break;

    files = build_files(CONFIG["path"]["software_files"], CONFIG["software"]["extension"], lng_key)
    for filename in files:
        try:
            file_name = os.path.basename(filename)
            file_name = file_name.replace("." + CONFIG["software"]["extension"], "")
            file = configparser.ConfigParser(allow_no_value=True, inline_comment_prefixes="#")
            file.sections()
            file_handler = open(filename)
            file_string = file_handler.read()
            file_handler.close() 
            if CONFIG["config_process"].getboolean("internal"):
                file_string = process_variable(file_string)
                file_string = process_if(file_string)
                file_string = process_cleanup(file_string)
            file.read_string(file_string)
        except:
            error.append("Error in file: " + file_name)
            continue

        if not file.has_option("main", "enabled"): continue
        if not file["main"].getboolean("enabled"): continue

        if file.has_option("main", "require") and CONFIG["software_process"].getboolean("require"):
            if not process_require(file["main"]["require"]): continue

        if file.has_option("main", "require_mode") and CONFIG["software_process"].getboolean("require_mode"):
            if not process_require_mode(file["main"]["require_mode"]): continue

        if file.has_option("main", "require_system") and CONFIG["software_process"].getboolean("require_system"):
            if not VARIABLES_SYSTEM.require(file["main"]["require_system"]): continue

        if file.has_option("main", "require_user") and CONFIG["software_process"].getboolean("require_user"):
            if not VARIABLES_USER.require(file["main"]["require_user"]): continue

        page_current = config_get(file, "main", "page", "", lng_key)
        if page_current != "" and page != "" and page_current != page: continue

        group_current = config_get(file, "main", "group", None, lng_key)

        for section in source.sections():
            if CONFIG["software"]["delimiter_variable"] +"group"+CONFIG["software"]["delimiter_variable"]  in section and (not group or group == group_current):
                continue

            section_key = section
            section_key = section_key.replace(CONFIG["software"]["delimiter_variable"] + "file" + CONFIG["software"]["delimiter_variable"], file_name)
            section_key = section_key.replace(CONFIG["software"]["delimiter_variable"] + "group", group_current)
            section_key = build_interface_software_replace(file, section_key, lng_key)
            section_key = build_variables_regex(section_key)

            if not dest.has_section(section_key):
                dest.add_section(section_key)

            for (key, val) in source.items(section):
                key = key.replace(CONFIG["software"]["delimiter_variable"] + "file" + CONFIG["software"]["delimiter_variable"], file_name)
                key = build_interface_software_replace(file, key, lng_key)
                val = val.replace(CONFIG["software"]["delimiter_variable"] + "file" + CONFIG["software"]["delimiter_variable"], file_name)
                val = build_interface_software_replace(file, val, lng_key)
                dest[section_key][key] = val
        group = group_current

    return dest




def build_interface_software_replace(file, string, lng_key=""):
    delimiter = CONFIG["software"]["delimiter_variable"]
    for section in file.sections():
        if section == "version": continue
        for (key, val) in file.items(section):
            if lng_key in key:
                key = key.replace(lng_key, "")
                string = string.replace(delimiter + key + delimiter, val)
        for (key, val) in file.items(section):
            string = string.replace(delimiter + key + delimiter, val)
    return string




def build_interface_wizard(source, lng_key=""):
    error = []

    dest = configparser.ConfigParser(allow_no_value=True, inline_comment_prefixes="#")
    dest.sections()

    group = None

    page = ""
    for section in source.sections():
        page = config_get(source, section, "page", "", lng_key)
        if page != "":
            if matches := re.match(r'(.*)(\s+)?[\\](\s+)?(.*)', page):
                page = matches.group(1)
            break;

    files = build_files(CONFIG["path"]["wizard_files"], CONFIG["wizard"]["extension"], lng_key)
    for filename in files:
        try:
            file_name = os.path.basename(filename)
            file_name = file_name.replace("." + CONFIG["wizard"]["extension"], "")
            file = configparser.ConfigParser(allow_no_value=True, inline_comment_prefixes="#")
            file.sections()
            file_handler = open(filename)
            file_string = file_handler.read()
            file_handler.close() 
            if CONFIG["config_process"].getboolean("internal"):
                file_string = process_variable(file_string)
                file_string = process_if(file_string)
                file_string = process_cleanup(file_string)
            file.read_string(file_string)
        except:
            error.append("Error in file: " + file_name)
            continue

        if not file.has_option("main", "enabled"): continue
        if not file["main"].getboolean("enabled"): continue

        if file.has_option("main", "require") and CONFIG["wizard_process"].getboolean("require"):
            if not process_require(file["main"]["require"]): continue

        if file.has_option("main", "require_mode") and CONFIG["wizard_process"].getboolean("require_mode"):
            if not process_require_mode(file["main"]["require_mode"]): continue

        if file.has_option("main", "require_software") and CONFIG["wizard_process"].getboolean("require_software") and CONFIG["software"].getboolean("enabled"):
            if not process_software_require(file["main"]["require_software"]): continue

        if file.has_option("main", "require_system") and CONFIG["wizard_process"].getboolean("require_system"):
            if not VARIABLES_SYSTEM.require(file["main"]["require_system"]): continue

        if file.has_option("main", "require_user") and CONFIG["wizard_process"].getboolean("require_user"):
            if not VARIABLES_USER.require(file["main"]["require_user"]): continue

        page_current = config_get(file, "main", "page", "", lng_key)
        if page_current != "" and page != "" and page_current != page: continue

        group_current = config_get(file, "main", "group", None, lng_key)

        for section in source.sections():
            if CONFIG["wizard"]["delimiter_variable"]+"group"+CONFIG["wizard"]["delimiter_variable"] in section and (not group or group == group_current):
                continue

            section_key = section
            section_key = section_key.replace(CONFIG["wizard"]["delimiter_variable"] + "file" + CONFIG["wizard"]["delimiter_variable"], file_name)
            section_key = section_key.replace(CONFIG["wizard"]["delimiter_variable"] + "group", group_current)
            section_key = build_interface_wizard_replace(file, section_key, lng_key)
            section_key = build_variables_regex(section_key)

            if not dest.has_section(section_key):
                dest.add_section(section_key)

            for (key, val) in source.items(section):
                key = key.replace(CONFIG["wizard"]["delimiter_variable"] + "file" + CONFIG["wizard"]["delimiter_variable"], file_name)
                key = build_interface_wizard_replace(file, key, lng_key)
                val = val.replace(CONFIG["wizard"]["delimiter_variable"] + "file" + CONFIG["wizard"]["delimiter_variable"], file_name)
                val = build_interface_wizard_replace(file, val, lng_key)
                dest[section_key][key] = val
        group = group_current

    return dest




def build_interface_wizard_replace(file, string, lng_key=""):
    delimiter = CONFIG["wizard"]["delimiter_variable"]
    for section in file.sections():
        if section == "version": continue
        for (key, val) in file.items(section):
            if lng_key in key:
                key = key.replace(lng_key, "")
                string = string.replace(delimiter + key + delimiter, val)
        for (key, val) in file.items(section):
            string = string.replace(delimiter + key + delimiter, val)
    return string




def build_interface_content(source):
    dest = copy.deepcopy(source)
    for key_root in source.keys():
        if isinstance(source[key_root], str):
            del dest[key_root]
            if CONFIG.has_option("interface_mapping", key_root):
                dest[CONFIG["interface_mapping"][key_root]] = source[key_root]
        else:
            for key in source[key_root].keys():
                del dest[key_root][key]
                if CONFIG.has_option("interface_mapping", key):
                    dest[key_root][CONFIG["interface_mapping"][key]] = source[key_root][key]
    return dest


##############################################################################################################
# Build config


def build_config(lng=""):
    global CONFIG_FILES
    global CONFIG_VARIABLES

    error = []

    CONFIG_FILES = defaultdict(lambda : defaultdict(lambda : defaultdict(dict)))
    CONFIG_VARIABLES = defaultdict(lambda : defaultdict(dict))

    config_system_sections = CONFIG["config"]["system_sections"].split(";")

    files = build_files(CONFIG["path"]["config_files"], CONFIG["config"]["extension"], lng)
    for filename in files:
        try:
            file_name = os.path.basename(filename)
            file = configparser.ConfigParser(allow_no_value=True, inline_comment_prefixes="#")
            file.sections()
            file_handler = open(filename)
            file_string = file_handler.read()
            file_handler.close()
            if CONFIG["config_process"].getboolean("internal"):
                file_string = process_variable(file_string)
                file_string = process_if(file_string)
                file_string = process_cleanup(file_string)
            file.read_string(file_string)
        except:
            error.append("Error in file: " + file_name)
            continue

        if not file.has_option("main", "enabled"): continue
        if not file["main"].getboolean("enabled"): continue

        if file.has_option("main", "require") and CONFIG["config_process"].getboolean("require"):
            if not process_require(file["main"]["require"]): continue

        if file.has_option("main", "require_software") and CONFIG["config_process"].getboolean("require_software") and CONFIG["software"].getboolean("enabled"):
            if not process_software_require(file["main"]["require_software"]): continue

        if file.has_option("main", "require_system") and CONFIG["config_process"].getboolean("require_system"):
            if not VARIABLES_SYSTEM.require(file["main"]["require_system"]): continue

        if file.has_option("main", "require_user") and CONFIG["config_process"].getboolean("require_user"):
            if not VARIABLES_USER.require(file["main"]["require_user"]): continue

        if file.has_option("main", "type"):
            if file["main"]["type"] != "config":
                continue

        for section in file.sections():
            if file.has_section("global") and section not in config_system_sections:
                for (key, val) in file.items("global"):
                    file[section][key] = val

            if file.has_option(section, "enabled"):
                if not file[section].getboolean("enabled"):
                    continue

            if file.has_option(section, "require") and CONFIG["config_process"].getboolean("require"):
                if not process_require(file[section]["require"]): continue

            if file.has_option(section, "require_software") and CONFIG["config_process"].getboolean("require_software") and CONFIG["software"].getboolean("enabled"):
                if not process_software_require(file[section]["require_software"]): continue

            if file.has_option(section, "require_system") and CONFIG["config_process"].getboolean("require_system"):
                if not VARIABLES_SYSTEM.require(file[section]["require_system"]): continue

            if file.has_option(section, "require_user") and CONFIG["config_process"].getboolean("require_user"):
                if not VARIABLES_USER.require(file[section]["require_user"]): continue

            section_key = build_variables_regex(section)
            if section_key in config_system_sections:
                for (key, val) in file.items(section):
                    CONFIG_FILES[file_name][section_key][key] = val
            else:
                sections = build_sections(file, section)
                if sections:
                    if not isinstance(sections, bool):
                        for sections_key in sections:
                            file[section]["file_section"] = sections[sections_key]["file_section"]
                            file[section]["file_key"] = sections[sections_key]["file_key"]
                            file[section]["file_subkey"] = sections[sections_key]["file_subkey"]
                            section_key = build_variables_regex(section + "_" + sections_key)
                            for (key, val) in file.items(section):
                                CONFIG_VARIABLES[section_key][key] = val.replace(CONFIG["config"]["delimiter_sections"], sections_key)
                else:
                    for (key, val) in file.items(section):
                        CONFIG_VARIABLES[section_key][key] = val
    return error


##############################################################################################################
# Build setions


def build_sections(config, section):
    if config.has_option(section, "files"):
        if config[section]["files"] != "":
            files = config[section]["files"]
            if not files.startswith("/"):
                files = PATH + "/" + files
            files = sorted(glob.glob(files, recursive=False))
            if len(files) > 0:
                result = defaultdict(lambda : defaultdict(lambda : defaultdict(dict)))
                regex = ""
                if config.has_option(section, "files_regex"):
                    if config[section]["files_regex"] != "":
                        regex = config[section]["files_regex"]
                for file in files:
                    filename = os.path.basename(file)
                    if re.search(regex, filename):
                        result[filename]["file_section"] = ""
                        result[filename]["file_key"] = ""
                        result[filename]["file_subkey"] = ""
                if len(result) > 0:
                    return result
        return True

    if config.has_option(section, "file") and not (config.has_option(section, "file_section") or config.has_option(section, "file_key")):
        file_parts = config[section]["file"].split("\\")
        if len(file_parts) == 2:
            config[section]["file"] = file_parts[0]
            config[section]["file_section"] = file_parts[1]
            config[section]["file_key"] = ""
            config[section]["file_subkey"] = ""
        elif len(file_parts) == 3:
            config[section]["file"] = file_parts[0]
            config[section]["file_section"] = file_parts[1]
            config[section]["file_key"] = file_parts[2]
            config[section]["file_subkey"] = ""
        elif len(file_parts) == 4:
            config[section]["file"] = file_parts[0]
            config[section]["file_section"] = file_parts[1]
            config[section]["file_key"] = file_parts[2]
            config[section]["file_subkey"] = file_parts[3]

    if not config.has_option(section, "file_subkey"):
        config[section]["file_subkey"] = ""

    if config.has_option(section, "file") and config.has_option(section, "file_section") and config.has_option(section, "file_key") and config.has_option(section, "file_subkey"):
        if CONFIG["config"]["delimiter_sections"] in config[section]["file_section"] or CONFIG["config"]["delimiter_sections"] in config[section]["file_key"] or CONFIG["config"]["delimiter_sections"] in config[section]["file_subkey"]:
            result = build_sections_detail(config[section]["file"], config["files"][config[section]["file"]], config[section]["file_section"], config[section]["file_key"], config[section]["file_subkey"], CONFIG["config"]["delimiter_sections"])
            if result:
                return result
            else:
                return True
    return False




def build_sections_detail(file_template, file_config, file_section, file_key, file_subkey, delimiter):
    result = defaultdict(lambda : defaultdict(lambda : defaultdict(dict)))

    file_open = file_config
    if CONFIG["main"].getboolean("mode_test"):
        file_open = CONFIG["path"]["mode_test"] + file_open
    if not os.path.exists(file_open):
        file_open = CONFIG["path"]["config_templates"] + "/" + file_template
    if not os.path.exists(file_open):
        return result
        
    if CONFIG["config_process"].getboolean("ini_raw") and CONFIG.has_option("config", "delimiter_variable_raw"):
        if CONFIG["config"]["delimiter_variable_raw"] != "":
            try:
                with open(file_open, 'r') as file:
                    text = file.read()
                    text_search = "\n" + text + "\n"
                    if regex := re.findall(r'[^'+CONFIG["config"]["delimiter_variable_raw"][0]+']('+CONFIG["config"]["delimiter_variable_raw"]+'(.*[^\s])'+CONFIG["config"]["delimiter_variable_raw"]+'((\n|.)*?)'+CONFIG["config"]["delimiter_variable_raw"]+')[^'+CONFIG["config"]["delimiter_variable_raw"][0]+']', text_search):
                        for match in regex:
                            text = text.replace(match[0], "")
                        file_open = text.splitlines()
            except:
                None

    try:
        config = ConfigObj(file_open, file_error=True, write_empty_values=True, encoding="utf8")
    except:
        return result

    if file_section == delimiter and file_key != delimiter and file_subkey != delimiter:
        for file_section in config:
            if file_key in config[file_section]:
                if file_subkey != "":
                    if file_subkey in config[file_section][file_key]:
                        result[file_section]["file_section"] = file_section
                        result[file_section]["file_key"] = file_key
                        result[file_section]["file_subkey"] = file_subkey
                else:
                    result[file_section]["file_section"] = file_section
                    result[file_section]["file_key"] = file_key
                    result[file_section]["file_subkey"] = ""
        return result

    elif file_section != delimiter and file_key == delimiter and file_subkey != delimiter:
        if file_section in config:
            for file_key in config[file_section]:
                if file_subkey != "":
                    if file_subkey in config[file_section][file_key]:
                        result[file_key]["file_section"] = file_section
                        result[file_key]["file_key"] = file_key
                        result[file_key]["file_subkey"] = file_subkey
                else:
                    result[file_key]["file_section"] = file_section
                    result[file_key]["file_key"] = file_key
                    result[file_key]["file_subkey"] = ""
            return result

    elif file_section == delimiter and file_key == delimiter and file_subkey != delimiter:
        for file_section in config:
            for file_key in config[file_section]:
                if file_subkey != "":
                    if file_subkey in config[file_section][file_key]:
                        result[file_section+file_key]["file_section"] = file_section
                        result[file_section+file_key]["file_key"] = file_key
                        result[file_section+file_key]["file_subkey"] = file_subkey
                else:
                    result[file_section+file_key]["file_section"] = file_section
                    result[file_section+file_key]["file_key"] = file_key
                    result[file_section+file_key]["file_subkey"] = ""
        return result

    elif file_section == delimiter and file_key == delimiter and file_subkey== delimiter:
        for file_section in config:
            for file_key in config[file_section]:
                for file_subkey in config[file_section][file_key]:
                    result[file_section+file_key+file_subkey]["file_section"] = file_section
                    result[file_section+file_key+file_subkey]["file_key"] = file_key
                    result[file_section+file_key+file_subkey]["file_subkey"] = file_subkey
        return result

    return result


##############################################################################################################
# Build data


def build_data(lng=""):
    global VARIABLES_DATA

    error = []

    VARIABLES_DATA = defaultdict(dict)

    config_system_sections = CONFIG["config"]["system_sections"].split(";")

    files = build_files(CONFIG["path"]["config_files"], CONFIG["config"]["extension"], lng)
    for filename in files:
        try:
            file_name = os.path.basename(filename)
            file = configparser.ConfigParser(allow_no_value=True, inline_comment_prefixes="#")
            file.sections()
            file_handler = open(filename)
            file_string = file_handler.read()
            file_handler.close()
            if CONFIG["config_process"].getboolean("internal"):
                file_string = process_variable(file_string)
                file_string = process_if(file_string)
                file_string = process_cleanup(file_string)
            file.read_string(file_string)
        except:
            error.append("Error in file: " + file_name)
            continue

        if not file.has_option("main", "enabled"): continue
        if not file["main"].getboolean("enabled"): continue

        if file.has_option("main", "require") and CONFIG["config_process"].getboolean("require"):
            if not process_require(file["main"]["require"]): continue

        if file.has_option("main", "require_software") and CONFIG["config_process"].getboolean("require_software") and CONFIG["software"].getboolean("enabled"):
            if not process_software_require(file["main"]["require_software"]): continue

        if file.has_option("main", "require_system") and CONFIG["config_process"].getboolean("require_system"):
            if not VARIABLES_SYSTEM.require(file["main"]["require_system"]): continue

        if file.has_option("main", "require_user") and CONFIG["config_process"].getboolean("require_user"):
            if not VARIABLES_USER.require(file["main"]["require_user"]): continue

        if file.has_option("main", "type"):
            if file["main"]["type"] != "config":
                continue

        for section in file.sections():
            if file.has_section("global") and section not in config_system_sections:
                for (key, val) in file.items("global"):
                    file[section][key] = val

            if file.has_option(section, "enabled"):
                if not file[section].getboolean("enabled"):
                    continue

            if file.has_option(section, "require") and CONFIG["config_process"].getboolean("require"):
                if not process_require(file[section]["require"]): continue

            if file.has_option(section, "require_software") and CONFIG["config_process"].getboolean("require_software") and CONFIG["software"].getboolean("enabled"):
                if not process_software_require(file[section]["require_software"]): continue

            if file.has_option(section, "require_system") and CONFIG["config_process"].getboolean("require_system"):
                if not VARIABLES_SYSTEM.require(file[section]["require_system"]): continue

            if file.has_option(section, "require_user") and CONFIG["config_process"].getboolean("require_user"):
                if not VARIABLES_USER.require(file[section]["require_user"]): continue

            section_key = build_variables_regex(section)
            if section_key in config_system_sections:
                continue

            if file.has_option(section, "value"):
                sections = build_sections(file, section)
                if sections:
                    if not isinstance(sections, bool):
                        for sections_key in sections:
                            section_key = build_variables_regex(section + "_" + sections_key)
                            VARIABLES_DATA[section_key] = file[section]["value"]
                else:
                    VARIABLES_DATA[section_key] = file[section]["value"]
    return error


##############################################################################################################
# Build software


def build_software(lng=""):
    global VARIABLES_SOFTWARE

    error = []

    VARIABLES_SOFTWARE = defaultdict(lambda : defaultdict(dict))
    VARIABLES_SOFTWARE["package"] = {}
    VARIABLES_SOFTWARE["package_version"] = {}
    VARIABLES_SOFTWARE["package_raw"] = ""
    VARIABLES_SOFTWARE["python"] = {}
    VARIABLES_SOFTWARE["python_version"] = {}
    VARIABLES_SOFTWARE["python_raw"] = ""
    VARIABLES_SOFTWARE["software"] = {}
    VARIABLES_SOFTWARE["software_version"] = {}
    VARIABLES_SOFTWARE["software_raw"] = ""

    if not CONFIG["software"].getboolean("enabled"): return True

    lng_key, lng_delimiter = build_lng(lng)

    if CONFIG.has_option("software_process", "package_status_cmd_before"):
        if CONFIG["software_process"]["package_status_cmd_before"] != "":
            execute_cmd(CONFIG["software_process"]["package_status_cmd_before"])
    try:
        result = subprocess.run("apt list --installed", capture_output=True, shell=True, text=True)
        if result.returncode == 0:
            regex = re.findall(r'(.*)\/.*now\s(\d+:)?([\w\.\-\+]+)', result.stdout)
            for match in regex:
                VARIABLES_SOFTWARE["package"][match[0].lower()] = True
                VARIABLES_SOFTWARE["package_version"][match[0].lower()] = match[2]
            VARIABLES_SOFTWARE["package_raw"] = result.stdout
            VARIABLES_SOFTWARE["package_raw"] = VARIABLES_SOFTWARE["package_raw"].replace("Listing...\n", "")
    except:
        None
    if CONFIG.has_option("software_process", "package_status_cmd_after"):
        if CONFIG["software_process"]["package_status_cmd_after"] != "":
            execute_cmd(CONFIG["software_process"]["package_status_cmd_after"])

    if CONFIG.has_option("software_process", "python_status_cmd_before"):
        if CONFIG["software_process"]["python_status_cmd_before"] != "":
            execute_cmd(CONFIG["software_process"]["python_status_cmd_before"])
    python_raw = []
    for pkg in pkg_resources.working_set:
        VARIABLES_SOFTWARE["python"][pkg.key.lower()] = True
        VARIABLES_SOFTWARE["python_version"][pkg.key.lower()] = pkg.version
        python_raw.append(pkg.key + " " + pkg.version)
    VARIABLES_SOFTWARE["python_raw"] = "\n".join(sorted(python_raw))
    if CONFIG.has_option("software_process", "python_status_cmd_after"):
        if CONFIG["software_process"]["python_status_cmd_after"] != "":
            execute_cmd(CONFIG["software_process"]["python_status_cmd_after"])

    files = build_files(CONFIG["path"]["software_files"], CONFIG["software"]["extension"], lng)
    for filename in files:
        try:
            file_name = os.path.basename(filename)
            file_name = file_name.replace("." + CONFIG["software"]["extension"], "")
            file = configparser.ConfigParser(allow_no_value=True, inline_comment_prefixes="#")
            file.sections()
            file_handler = open(filename)
            file_string = file_handler.read()
            file_handler.close() 
            file.read_string(file_string)
        except:
            error.append("Error in file: " + file_name)
            continue

        if not file.has_option("main", "enabled"): continue
        if not file["main"].getboolean("enabled"): continue

        if file.has_option("main", "require") and CONFIG["software_process"].getboolean("require"):
            if not process_require(file["main"]["require"]): continue

        if file.has_option("main", "require_system") and CONFIG["software_process"].getboolean("require_system"):
            if not VARIABLES_SYSTEM.require(file["main"]["require_system"]): continue

        if file.has_option("main", "require_user") and CONFIG["software_process"].getboolean("require_user"):
            if not VARIABLES_USER.require(file["main"]["require_user"]): continue

        valid = True

        config = config_get(file, "package", "status", "", lng_key)
        if config == "": config = config_get(file, "package", "name", "", lng_key)
        if config != "":
            config = config.lower()
            config = config.replace(" ", ";")
            config = config.replace(",", ";")
            config = config.split(";")
            for x in config:
                x = x.strip()
                if x not in VARIABLES_SOFTWARE["package"]: valid = False

        config = config_get(file, "python", "status", "", lng_key)
        if config == "": config = config_get(file, "python", "name", "", lng_key)
        if config != "":
            config = config.lower()
            config = config.replace(" ", ";")
            config = config.replace(",", ";")
            config = config.split(";")
            for x in config:
                x = x.strip()
                if x not in VARIABLES_SOFTWARE["python"]: valid = False

        if valid:
            VARIABLES_SOFTWARE["software"][file_name] = True
            VARIABLES_SOFTWARE["software_version"][file_name] = ""
            if file.has_section("version"):
                if file.has_option("version", "number"):
                    VARIABLES_SOFTWARE["software_version"][file_name] = file["version"]["number"]
            VARIABLES_SOFTWARE["software_raw"] = VARIABLES_SOFTWARE["software_raw"] + file_name + " " + VARIABLES_SOFTWARE["software_version"][file_name] + "\n"

    return error


##############################################################################################################
# User


def user_get(file):
    global CONFIG_AUTH
    if not CONFIG_AUTH:
        if not config_auth_read(file):
            log("Config - Error reading config file " + PATH + "/config_auth.cfg", LOG_ERROR)
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
# Data


def data_read_file():
    for file_name in CONFIG_FILES.keys():
        for file in CONFIG_FILES[file_name]["files_type"].keys():
            if not isinstance(CONFIG_FILES[file_name]["files_type"][file], str) or not isinstance(CONFIG_FILES[file_name]["files"][file], str): continue

            type = CONFIG_FILES[file_name]["files_type"][file]

            if type == "env":
                data_read_file_env("", file, False)
            elif type == "env_edit":
                data_read_file_env(CONFIG_FILES[file_name]["files"][file], file, True)
            elif type == "ini":
                data_read_file_ini("", file, False)
            elif type == "ini_edit":
                data_read_file_ini(CONFIG_FILES[file_name]["files"][file], file, True)
            elif type == "json":
                data_read_file_json("", file, False)
            elif type == "json_edit":
                data_read_file_json(CONFIG_FILES[file_name]["files"][file], file, True)
            elif type == "keyarg":
                data_read_file_keyarg("", file, False)
            elif type == "keyarg_edit":
                data_read_file_keyarg(CONFIG_FILES[file_name]["files"][file], file, True)
            elif type == "keyval":
                data_read_file_keyval("", file, False)
            elif type == "keyval_edit":
                data_read_file_keyval(CONFIG_FILES[file_name]["files"][file], file, True)
            elif type == "raw":
                data_read_file_raw("", file, False)
            elif type == "raw_edit":
                data_read_file_raw(CONFIG_FILES[file_name]["files"][file], file, True)
            elif type == "toml":
                data_read_file_toml("", file, False)
            elif type == "toml_edit":
                data_read_file_toml(CONFIG_FILES[file_name]["files"][file], file, True)
            elif type == "xml":
                data_read_file_xml("", file, False)
            elif type == "xml_edit":
                data_read_file_xml(CONFIG_FILES[file_name]["files"][file], file, True)
            elif type == "yaml":
                data_read_file_yaml("", file, False)
            elif type == "yaml_edit":
                data_read_file_yaml(CONFIG_FILES[file_name]["files"][file], file, True)
    return True




def data_read_file_env(source, file, update=True):
    if not CONFIG["config_process"].getboolean("env_read"): return True

    global VARIABLES_DATA

    if file == "": return

    if source == "":
        source = CONFIG["path"]["config_templates"] + "/" + file
    else:
        if CONFIG["main"].getboolean("mode_test"):
            source = CONFIG["path"]["mode_test"] + source
        if not os.path.exists(source):
            source = CONFIG["path"]["config_templates"] + "/" + file

    if not os.path.exists(source):
        return

    if CONFIG["config_process"].getboolean("env_raw") and CONFIG.has_option("config", "delimiter_variable_raw"):
        if CONFIG["config"]["delimiter_variable_raw"] != "":
            raw_keys = []
            for key in VARIABLES_DATA.keys():
                if isinstance(CONFIG_VARIABLES[key]["file"], str) and not isinstance(CONFIG_VARIABLES[key]["file_section"], str):
                    if CONFIG_VARIABLES[key]["file"] != "" and CONFIG_VARIABLES[key]["file"] == file:
                        raw_keys.append(key)
            if len(raw_keys) > 0:
                try:
                    with open(source, 'r') as source_file:
                        text = source_file.read()
                        text_search = "\n" + text + "\n"
                        text_executed = False
                        for key in raw_keys:
                           if regex := re.findall(r'[^'+CONFIG["config"]["delimiter_variable_raw"][0]+']('+CONFIG["config"]["delimiter_variable_raw"]+'('+key+')'+CONFIG["config"]["delimiter_variable_raw"]+'((\n|.)*?)'+CONFIG["config"]["delimiter_variable_raw"]+')[^'+CONFIG["config"]["delimiter_variable_raw"][0]+']', text_search):
                                for match in regex:
                                    VARIABLES_DATA[key] = match[2].strip()
                                    text = text.replace(match[0], "")
                                    text_executed = True
                        if text_executed: source = text.splitlines()
                except:
                    None

    try:
        source_file = open(source, "r")
        text = source_file.read()
        source_file.close()
    except:
        return

    for key in VARIABLES_DATA.keys():
        if not update and isinstance(CONFIG_VARIABLES[key]["config_current"], str): continue
        if isinstance(CONFIG_VARIABLES[key]["file"], str) and isinstance(CONFIG_VARIABLES[key]["file_section"], str):
            if CONFIG_VARIABLES[key]["file"] != "" and CONFIG_VARIABLES[key]["file_section"] != "":
                if CONFIG_VARIABLES[key]["file"] == file:
                    if group := re.search(r'^('+CONFIG_VARIABLES[key]["file_section"]+')=(.*)', text, flags=re.M):
                        VARIABLES_DATA[key] = group[2]
                        if VARIABLES_DATA[key].startswith('"') and VARIABLES_DATA[key].endswith('"'): VARIABLES_DATA[key] = VARIABLES_DATA[key].lstrip('"').rstrip('"')




def data_read_file_ini(source, file, update=True):
    if not CONFIG["config_process"].getboolean("ini_read"): return True

    global VARIABLES_DATA

    if file == "": return

    if source == "":
        source = CONFIG["path"]["config_templates"] + "/" + file
    else:
        if CONFIG["main"].getboolean("mode_test"):
            source = CONFIG["path"]["mode_test"] + source
        if not os.path.exists(source):
            source = CONFIG["path"]["config_templates"] + "/" + file

    if not os.path.exists(source):
        return

    if CONFIG["config_process"].getboolean("ini_raw") and CONFIG.has_option("config", "delimiter_variable_raw"):
        if CONFIG["config"]["delimiter_variable_raw"] != "":
            raw_keys = []
            for key in VARIABLES_DATA.keys():
                if isinstance(CONFIG_VARIABLES[key]["file"], str) and not isinstance(CONFIG_VARIABLES[key]["file_section"], str) and not isinstance(CONFIG_VARIABLES[key]["file_key"], str):
                    if CONFIG_VARIABLES[key]["file"] != "" and CONFIG_VARIABLES[key]["file"] == file:
                        raw_keys.append(key)
            if len(raw_keys) > 0:
                try:
                    with open(source, 'r') as source_file:
                        text = source_file.read()
                        text_search = "\n" + text + "\n"
                        text_executed = False
                        for key in raw_keys:
                           if regex := re.findall(r'[^'+CONFIG["config"]["delimiter_variable_raw"][0]+']('+CONFIG["config"]["delimiter_variable_raw"]+'('+key+')'+CONFIG["config"]["delimiter_variable_raw"]+'((\n|.)*?)'+CONFIG["config"]["delimiter_variable_raw"]+')[^'+CONFIG["config"]["delimiter_variable_raw"][0]+']', text_search):
                                for match in regex:
                                    VARIABLES_DATA[key] = match[2].strip()
                                    text = text.replace(match[0], "")
                                    text_executed = True
                        if text_executed: source = text.splitlines()
                except:
                    None

    try:
        config = ConfigObj(source, file_error=True, write_empty_values=True, encoding="utf8")
    except:
        return

    for key in VARIABLES_DATA.keys():
        if not update and isinstance(CONFIG_VARIABLES[key]["config_current"], str): continue
        if isinstance(CONFIG_VARIABLES[key]["file"], str) and isinstance(CONFIG_VARIABLES[key]["file_section"], str) and isinstance(CONFIG_VARIABLES[key]["file_key"], str):
            if CONFIG_VARIABLES[key]["file"] != "" and CONFIG_VARIABLES[key]["file_section"] != "" and CONFIG_VARIABLES[key]["file_key"] != "":
                if CONFIG_VARIABLES[key]["file"] == file:
                    if isinstance(CONFIG_VARIABLES[key]["file_subkey"], str):
                        if CONFIG_VARIABLES[key]["file_subkey"] != "":
                            if CONFIG_VARIABLES[key]["file_section"] in config and CONFIG_VARIABLES[key]["file_key"] in config[CONFIG_VARIABLES[key]["file_section"]] and CONFIG_VARIABLES[key]["file_subkey"] in config[CONFIG_VARIABLES[key]["file_section"]][CONFIG_VARIABLES[key]["file_key"]]:
                                if isinstance(config[CONFIG_VARIABLES[key]["file_section"]][CONFIG_VARIABLES[key]["file_key"]][CONFIG_VARIABLES[key]["file_subkey"]], str):
                                    VARIABLES_DATA[key] = config[CONFIG_VARIABLES[key]["file_section"]][CONFIG_VARIABLES[key]["file_key"]][CONFIG_VARIABLES[key]["file_subkey"]]
                        else:
                            if CONFIG_VARIABLES[key]["file_section"] in config and CONFIG_VARIABLES[key]["file_key"] in config[CONFIG_VARIABLES[key]["file_section"]]:
                                if isinstance(config[CONFIG_VARIABLES[key]["file_section"]][CONFIG_VARIABLES[key]["file_key"]], str):
                                    VARIABLES_DATA[key] = config[CONFIG_VARIABLES[key]["file_section"]][CONFIG_VARIABLES[key]["file_key"]]
                    else:
                        if CONFIG_VARIABLES[key]["file_section"] in config and CONFIG_VARIABLES[key]["file_key"] in config[CONFIG_VARIABLES[key]["file_section"]]:
                            if isinstance(config[CONFIG_VARIABLES[key]["file_section"]][CONFIG_VARIABLES[key]["file_key"]], str):
                                VARIABLES_DATA[key] = config[CONFIG_VARIABLES[key]["file_section"]][CONFIG_VARIABLES[key]["file_key"]]




def data_read_file_json(source, file, update=True):
    if not CONFIG["config_process"].getboolean("json_read"): return True

    global VARIABLES_DATA

    if file == "": return

    if source == "":
        source = CONFIG["path"]["config_templates"] + "/" + file
    else:
        if CONFIG["main"].getboolean("mode_test"):
            source = CONFIG["path"]["mode_test"] + source
        if not os.path.exists(source):
            source = CONFIG["path"]["config_templates"] + "/" + file

    if not os.path.exists(source):
        return

    try:
        file_config = open(source, "r")
        config = json.load(file_config)
        file_config.close()
    except:
        return

    #todo




def data_read_file_keyarg(source, file, update=True):
    if not CONFIG["config_process"].getboolean("keyarg_read"): return True

    global VARIABLES_DATA

    if file == "": return

    if source == "":
        source = CONFIG["path"]["config_templates"] + "/" + file
    else:
        if CONFIG["main"].getboolean("mode_test"):
            source = CONFIG["path"]["mode_test"] + source
        if not os.path.exists(source):
            source = CONFIG["path"]["config_templates"] + "/" + file

    if not os.path.exists(source):
        return

    if CONFIG["config_process"].getboolean("keyarg_raw") and CONFIG.has_option("config", "delimiter_variable_raw"):
        if CONFIG["config"]["delimiter_variable_raw"] != "":
            raw_keys = []
            for key in VARIABLES_DATA.keys():
                if isinstance(CONFIG_VARIABLES[key]["file"], str) and not isinstance(CONFIG_VARIABLES[key]["file_section"], str):
                    if CONFIG_VARIABLES[key]["file"] != "" and CONFIG_VARIABLES[key]["file"] == file:
                        raw_keys.append(key)
            if len(raw_keys) > 0:
                try:
                    with open(source, 'r') as source_file:
                        text = source_file.read()
                        text_search = "\n" + text + "\n"
                        text_executed = False
                        for key in raw_keys:
                           if regex := re.findall(r'[^'+CONFIG["config"]["delimiter_variable_raw"][0]+']('+CONFIG["config"]["delimiter_variable_raw"]+'('+key+')'+CONFIG["config"]["delimiter_variable_raw"]+'((\n|.)*?)'+CONFIG["config"]["delimiter_variable_raw"]+')[^'+CONFIG["config"]["delimiter_variable_raw"][0]+']', text_search):
                                for match in regex:
                                    VARIABLES_DATA[key] = match[2].strip()
                                    text = text.replace(match[0], "")
                                    text_executed = True
                        if text_executed: source = text.splitlines()
                except:
                    None

    try:
        source_file = open(source, "r")
        text = source_file.read()
        source_file.close()
    except:
        return

    for key in VARIABLES_DATA.keys():
        if not update and isinstance(CONFIG_VARIABLES[key]["config_current"], str): continue
        if isinstance(CONFIG_VARIABLES[key]["file"], str) and isinstance(CONFIG_VARIABLES[key]["file_section"], str):
            if CONFIG_VARIABLES[key]["file"] != "" and CONFIG_VARIABLES[key]["file_section"] != "":
                if CONFIG_VARIABLES[key]["file"] == file:
                    if group := re.search(r'^((\s+)?'+CONFIG_VARIABLES[key]["file_section"]+')\s(.*)', text, flags=re.M):
                        VARIABLES_DATA[key] = group[3]
                        if VARIABLES_DATA[key].startswith('"') and VARIABLES_DATA[key].endswith('"'): VARIABLES_DATA[key] = VARIABLES_DATA[key].lstrip('"').rstrip('"')




def data_read_file_keyval(source, file, update=True):
    if not CONFIG["config_process"].getboolean("keyval_read"): return True

    global VARIABLES_DATA

    if file == "": return

    if source == "":
        source = CONFIG["path"]["config_templates"] + "/" + file
    else:
        if CONFIG["main"].getboolean("mode_test"):
            source = CONFIG["path"]["mode_test"] + source
        if not os.path.exists(source):
            source = CONFIG["path"]["config_templates"] + "/" + file

    if not os.path.exists(source):
        return

    if CONFIG["config_process"].getboolean("keyval_raw") and CONFIG.has_option("config", "delimiter_variable_raw"):
        if CONFIG["config"]["delimiter_variable_raw"] != "":
            raw_keys = []
            for key in VARIABLES_DATA.keys():
                if isinstance(CONFIG_VARIABLES[key]["file"], str) and not isinstance(CONFIG_VARIABLES[key]["file_section"], str):
                    if CONFIG_VARIABLES[key]["file"] != "" and CONFIG_VARIABLES[key]["file"] == file:
                        raw_keys.append(key)
            if len(raw_keys) > 0:
                try:
                    with open(source, 'r') as source_file:
                        text = source_file.read()
                        text_search = "\n" + text + "\n"
                        text_executed = False
                        for key in raw_keys:
                           if regex := re.findall(r'[^'+CONFIG["config"]["delimiter_variable_raw"][0]+']('+CONFIG["config"]["delimiter_variable_raw"]+'('+key+')'+CONFIG["config"]["delimiter_variable_raw"]+'((\n|.)*?)'+CONFIG["config"]["delimiter_variable_raw"]+')[^'+CONFIG["config"]["delimiter_variable_raw"][0]+']', text_search):
                                for match in regex:
                                    VARIABLES_DATA[key] = match[2].strip()
                                    text = text.replace(match[0], "")
                                    text_executed = True
                        if text_executed: source = text.splitlines()
                except:
                    None

    try:
        source_file = open(source, "r")
        text = source_file.read()
        source_file.close()
    except:
        return

    for key in VARIABLES_DATA.keys():
        if not update and isinstance(CONFIG_VARIABLES[key]["config_current"], str): continue
        if isinstance(CONFIG_VARIABLES[key]["file"], str) and isinstance(CONFIG_VARIABLES[key]["file_section"], str):
            if CONFIG_VARIABLES[key]["file"] != "" and CONFIG_VARIABLES[key]["file_section"] != "":
                if CONFIG_VARIABLES[key]["file"] == file:
                    if group := re.search(r'^((\s+)?'+CONFIG_VARIABLES[key]["file_section"]+')(\s+)?=(\s+)?(.*)', text, flags=re.M):
                        VARIABLES_DATA[key] = group[5]




def data_read_file_raw(source, file, update=True):
    if not CONFIG["config_process"].getboolean("raw_read"): return True

    global VARIABLES_DATA

    if file == "": return

    if source == "":
        source = CONFIG["path"]["config_templates"] + "/" + file
    else:
        if CONFIG["main"].getboolean("mode_test"):
            source = CONFIG["path"]["mode_test"] + source
        if not os.path.exists(source):
            source = CONFIG["path"]["config_templates"] + "/" + file

    if not os.path.exists(source):
        return

    try:
        file_config = open(source, "r")
        config = file_config.read()
        file_config.close()
    except:
        return

    for key in VARIABLES_DATA.keys():
        if not update and isinstance(CONFIG_VARIABLES[key]["config_current"], str): continue
        if isinstance(CONFIG_VARIABLES[key]["file"], str):
            if CONFIG_VARIABLES[key]["file"] != "" and CONFIG_VARIABLES[key]["file"] == file:
                VARIABLES_DATA[key] = config




def data_read_file_toml(source, file, update=True):
    if not CONFIG["config_process"].getboolean("toml_read"): return True

    global VARIABLES_DATA

    if file == "": return

    if source == "":
        source = CONFIG["path"]["config_templates"] + "/" + file
    else:
        if CONFIG["main"].getboolean("mode_test"):
            source = CONFIG["path"]["mode_test"] + source
        if not os.path.exists(source):
            source = CONFIG["path"]["config_templates"] + "/" + file

    if not os.path.exists(source):
        return

    #todo




def data_read_file_xml(source, file, update=True):
    if not CONFIG["config_process"].getboolean("xml_read"): return True

    global VARIABLES_DATA

    if file == "": return

    if source == "":
        source = CONFIG["path"]["config_templates"] + "/" + file
    else:
        if CONFIG["main"].getboolean("mode_test"):
            source = CONFIG["path"]["mode_test"] + source
        if not os.path.exists(source):
            source = CONFIG["path"]["config_templates"] + "/" + file

    if not os.path.exists(source):
        return

    #todo




def data_read_file_yaml(source, file, update=True):
    if not CONFIG["config_process"].getboolean("yaml_read"): return True

    global VARIABLES_DATA

    if file == "": return

    if source == "":
        source = CONFIG["path"]["config_templates"] + "/" + file
    else:
        if CONFIG["main"].getboolean("mode_test"):
            source = CONFIG["path"]["mode_test"] + source
        if not os.path.exists(source):
            source = CONFIG["path"]["config_templates"] + "/" + file

    if not os.path.exists(source):
        return

    #todo




def data_read():
    global VARIABLES_DATA

    file = CONFIG["path"]["config"] + "/config_current." + CONFIG["config"]["extension"]
    if os.path.isfile(file):
        with open(file) as outfile:
            try:
                data = json.load(outfile)
                for key in data.keys():
                    if key in VARIABLES_DATA:
                        VARIABLES_DATA[key] = data[key]
                        CONFIG_VARIABLES[key]["config_current"] = "True"
            except:
                return False
    return True




def data_save():
    file = CONFIG["path"]["config"] + "/config_current." + CONFIG["config"]["extension"]
    try:
        with open(file, "w") as outfile:
            json.dump(VARIABLES_DATA, outfile)
    except:
        return False
    return True




def data_default():
    if build_data() and data_save():
        return True
    else:
        return False


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
def config_read(file=None, file_override=None):
    global CONFIG

    if file is None:
        return False
    else:
        CONFIG = configparser.ConfigParser(allow_no_value=True, inline_comment_prefixes="#")
        CONFIG.sections()
        if os.path.isfile(file):
            try:
                if file_override is None:
                    CONFIG.read(file, encoding='utf-8')
                elif os.path.isfile(file_override):
                    CONFIG.read([file, file_override], encoding='utf-8')
                else:
                    CONFIG.read(file, encoding='utf-8')
            except Exception as e:
                return False
        else:
            if not config_default(file=file, file_override=file_override):
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
def config_default(file=None, file_override=None):
    global CONFIG

    if file is None:
        return False
    elif DEFAULT_CONFIG != "":
        if file_override and DEFAULT_CONFIG_OVERRIDE != "":
            if not os.path.isdir(os.path.dirname(file_override)):
                try:
                    os.makedirs(os.path.dirname(file_override))
                except Exception:
                    return False
            if not os.path.exists(file_override):
                try:
                    config_file = open(file_override, "w")
                    config_file.write(DEFAULT_CONFIG_OVERRIDE)
                    config_file.close()
                except:
                    return False

        if not os.path.isdir(os.path.dirname(file)):
            try:
                os.makedirs(os.path.dirname(file))
            except Exception:
                return False
        try:
            config_file = open(file, "w")
            config_file.write(DEFAULT_CONFIG)
            config_file.close()
            if not config_read(file=file, file_override=file_override):
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
def config_auth_read(file=None, file_override=None):
    global CONFIG_AUTH

    if file is None:
        return False
    else:
        CONFIG_AUTH = configparser.ConfigParser(allow_no_value=True, inline_comment_prefixes="#")
        CONFIG_AUTH.sections()
        if os.path.isfile(file):
            try:
                if file_override is None:
                    CONFIG_AUTH.read(file, encoding='utf-8')
                elif os.path.isfile(file_override):
                    CONFIG_AUTH.read([file, file_override], encoding='utf-8')
                else:
                    CONFIG_AUTH.read(file, encoding='utf-8')
            except Exception as e:
                return False
        else:
            if not config_auth_default(file=file, file_override=file_override):
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
def config_auth_default(file=None, file_override=None):
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
            if not config_auth_read(file=file, file_override=file_override):
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
# Value convert

def val_to_bool(val):
    if val == "on" or val == "On" or val == "true" or val == "True" or val == "yes" or val == "Yes" or val == "1" or val == "open" or val == "opened" or val == "up":
        return True
    elif val == "off" or val == "Off" or val == "false" or val == "False" or val == "no" or val == "No" or val == "0" or val == "close" or val == "closed" or val == "down":
        return False
    elif val != "":
        return True
    else:
        return False


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
def setup(path=None, path_log=None, loglevel=None, service=False, mode_test=False):
    global PATH
    global LOG_LEVEL
    global LOG_FILE
    global VARIABLES_SYSTEM
    global VARIABLES_USER

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

    if not config_read(PATH + "/config.cfg", PATH + "/config_files/config.cfg.owr"):
        log("Config - Error reading config file " + PATH + "/config.cfg", LOG_ERROR)
        panic()

    if not config_auth_read(PATH + "/config_auth.cfg", PATH + "/config_files/config_auth.cfg.owr"):
        log("Config - Error reading config file " + PATH + "/config_auth.cfg", LOG_ERROR)
        panic()

    if not CONFIG.has_option("main", "mode_test"):
        CONFIG["main"]["mode_test"] = "False"

    if mode_test:
        CONFIG["main"]["mode_test"] = "True"

    if CONFIG["config_process"].getboolean("variables_system"):
        VARIABLES_SYSTEM = variables_system_class(CONFIG)
        if CONFIG.has_option("config_process", "variables_system_prefix"):
            VARIABLES_SYSTEM.prefix_set(CONFIG["config_process"]["variables_system_prefix"])

    if CONFIG["config_process"].getboolean("variables_user"):
        VARIABLES_USER = variables_user_class(CONFIG)
        if CONFIG.has_option("config_process", "variables_user_prefix"):
            VARIABLES_USER.prefix_set(CONFIG["config_process"]["variables_user_prefix"])




#### Setup #####
def setup_path():
    global CONFIG

    if not CONFIG["path"]["backup"].startswith("/"): CONFIG["path"]["backup"] = PATH + "/" + CONFIG["path"]["backup"]
    if not CONFIG["path"]["config"].startswith("/"): CONFIG["path"]["config"] = PATH + "/" + CONFIG["path"]["config"]
    if not CONFIG["path"]["config_files"].startswith("/"): CONFIG["path"]["config_files"] = PATH + "/" + CONFIG["path"]["config_files"]
    if not CONFIG["path"]["config_templates"].startswith("/"): CONFIG["path"]["config_templates"] = PATH + "/" + CONFIG["path"]["config_templates"]
    if not CONFIG["path"]["software"].startswith("/"): CONFIG["path"]["software"] = PATH + "/" + CONFIG["path"]["software"]
    if not CONFIG["path"]["software_files"].startswith("/"): CONFIG["path"]["software_files"] = PATH + "/" + CONFIG["path"]["software_files"]
    if not CONFIG["path"]["software_templates"].startswith("/"): CONFIG["path"]["software_templates"] = PATH + "/" + CONFIG["path"]["software_templates"]
    if not CONFIG["path"]["wizard"].startswith("/"): CONFIG["path"]["wizard"] = PATH + "/" + CONFIG["path"]["wizard"]
    if not CONFIG["path"]["wizard_files"].startswith("/"): CONFIG["path"]["wizard_files"] = PATH + "/" + CONFIG["path"]["wizard_files"]
    if not CONFIG["path"]["wizard_templates"].startswith("/"): CONFIG["path"]["wizard_templates"] = PATH + "/" + CONFIG["path"]["wizard_templates"]
    if not CONFIG["path"]["tmp"].startswith("/"): CONFIG["path"]["tmp"] = PATH + "/" + CONFIG["path"]["tmp"]
    if not CONFIG["path"]["mode_test"].startswith("/"): CONFIG["path"]["mode_test"] = PATH + "/" + CONFIG["path"]["mode_test"]
    if not CONFIG["path"]["terminal"].startswith("/"): CONFIG["path"]["terminal"] = PATH + "/" + CONFIG["path"]["terminal"]
    if not CONFIG["path"]["auth_external"].startswith("/"): CONFIG["path"]["backup"] = PATH + "/" + CONFIG["path"]["auth_external"]




#### Setup #####
def setup_variables():
    global VARIABLES_SESSION

    VARIABLES_SESSION = defaultdict(dict)
    VARIABLES_SESSION["uid"] = None
    VARIABLES_SESSION["mode"] = CONFIG["main"]["mode_interface"]
    file = CONFIG["path"]["config"] + "/session_current." + CONFIG["config"]["extension"]
    if os.path.isfile(file):
        with open(file) as outfile:
            try:
                data = json.load(outfile)
                for key in data.keys():
                    VARIABLES_SESSION[key] = data[key]
            except:
                None




#### Setup #####
def setup_log():
    global LOG_PREFIX

    if CONFIG["main"].getboolean("mode_test"):
        LOG_PREFIX = "[TEST MODE] "
        log("...............................................................................", LOG_NOTICE)
        log("No changes to files and no execution of cmd/script!", LOG_NOTICE)
        log("...............................................................................", LOG_NOTICE)

        CONFIG["config_process"]["files_create_path"] = "True"
        CONFIG["config_process"]["files_create_file"] = "True"

    log("...............................................................................", LOG_INFO)
    log("        Name: " + CONFIG["main"]["name"], LOG_INFO)
    log("              " + CONFIG["main"]["description"], LOG_INFO)
    log("Program File: " + __file__, LOG_INFO)
    log(" Config File: " + PATH + "/config.cfg", LOG_INFO)
    log("     Version: " + VERSION, LOG_INFO)
    log("   Copyright: " + COPYRIGHT, LOG_INFO)
    log("...............................................................................", LOG_INFO)




#### Setup #####
def setup_connection():
    if not CONFIG["connection"].getboolean("enabled"):
        return

    if CONFIG.has_option("connection_reticulum", "enabled"):
        if CONFIG["connection_reticulum"].getboolean("enabled"):
            from connection_reticulum import connection_reticulum_class
            #todo
            #reticulum = connection_webserver_aiohttp_class(host=CONFIG["connection_webserver_aiohttp"]["host"], port=CONFIG.getint("connection_webserver_aiohttp", "port"), path_get="/" + CONFIG["connection_webserver_aiohttp"]["path_get"], path_post="/" + CONFIG["connection_webserver_aiohttp"]["path_post"], path_root=PATH + "/" + CONFIG["connection_webserver_aiohttp"]["path_root"], path_tmp=PATH + "/" + CONFIG["connection_webserver_aiohttp"]["path_tmp"], headers=CONFIG["connection_webserver_aiohttp"]["headers"], auth=CONFIG["connection_webserver_aiohttp"].getboolean("auth"), redirect=CONFIG["connection_webserver_aiohttp"].getboolean("auth"), path_redirect_not_found=CONFIG["connection_webserver_aiohttp"]["path_redirect_not_found"], max_content_lenght=CONFIG.getint("connection_webserver_aiohttp", "max_content_lenght"))
            #reticulum.register_auth_callback(process_auth)
            #reticulum.register_get_callback(process_get)
            #reticulum.register_post_callback(process_post)
            #reticulum.start()

    if CONFIG.has_option("connection_webserver_aiohttp", "enabled"):
        if CONFIG["connection_webserver_aiohttp"].getboolean("enabled"):
            from connection_webserver_aiohttp import connection_webserver_aiohttp_class
            webserver = connection_webserver_aiohttp_class(host=CONFIG["connection_webserver_aiohttp"]["host"], port=CONFIG.getint("connection_webserver_aiohttp", "port"), path_get="/" + CONFIG["connection_webserver_aiohttp"]["path_get"], path_post="/" + CONFIG["connection_webserver_aiohttp"]["path_post"], path_root=PATH + "/" + CONFIG["connection_webserver_aiohttp"]["path_root"], path_tmp=PATH + "/" + CONFIG["connection_webserver_aiohttp"]["path_tmp"], headers=CONFIG["connection_webserver_aiohttp"]["headers"], options=CONFIG["connection_webserver_aiohttp"]["options"], auth=CONFIG["connection_webserver_aiohttp"].getboolean("auth"), redirect=CONFIG["connection_webserver_aiohttp"].getboolean("redirect"), path_redirect_root=CONFIG["connection_webserver_aiohttp"]["path_redirect_root"], path_redirect_not_found=CONFIG["connection_webserver_aiohttp"]["path_redirect_not_found"], max_content_lenght=CONFIG.getint("connection_webserver_aiohttp", "max_content_lenght"))
            webserver.register_auth_callback(process_auth)
            webserver.register_get_callback(process_get)
            webserver.register_post_callback(process_post)
            webserver.register_download_callback(process_download)
            webserver.register_upload_callback(process_upload)
            webserver.register_upload_auth_callback(process_upload_auth)
            webserver.start()

    if CONFIG.has_option("connection_webserver_flask", "enabled"):
        if CONFIG["connection_webserver_flask"].getboolean("enabled"):
            from connection_webserver_flask import connection_webserver_flask_class
            webserver = connection_webserver_flask_class(host=CONFIG["connection_webserver_flask"]["host"], port=CONFIG.getint("connection_webserver_flask", "port"), path_get="/" + CONFIG["connection_webserver_flask"]["path_get"], path_post="/" + CONFIG["connection_webserver_flask"]["path_post"], path_root=PATH + "/" + CONFIG["connection_webserver_flask"]["path_root"], path_tmp=PATH + "/" + CONFIG["connection_webserver_flask"]["path_tmp"], headers=CONFIG["connection_webserver_flask"]["headers"], options=CONFIG["connection_webserver_flask"]["options"], auth=CONFIG["connection_webserver_flask"].getboolean("auth"), redirect=CONFIG["connection_webserver_flask"].getboolean("redirect"), path_redirect_root=CONFIG["connection_webserver_flask"]["path_redirect_root"], path_redirect_not_found=CONFIG["connection_webserver_flask"]["path_redirect_not_found"], max_content_lenght=CONFIG.getint("connection_webserver_flask", "max_content_lenght"))
            webserver.register_auth_callback(process_auth)
            webserver.register_get_callback(process_get)
            webserver.register_post_callback(process_post)
            webserver.register_download_callback(process_download)
            webserver.register_upload_callback(process_upload)
            webserver.register_upload_auth_callback(process_upload_auth)
            webserver.start()

    if CONFIG.has_option("connection_webserver_gunicorn", "enabled"):
        if CONFIG["connection_webserver_gunicorn"].getboolean("enabled"):
            from connection_webserver_gunicorn import connection_webserver_gunicorn_class
            webserver = connection_webserver_gunicorn_class(host=CONFIG["connection_webserver_gunicorn"]["host"], port=CONFIG.getint("connection_webserver_gunicorn", "port"), path_get="/" + CONFIG["connection_webserver_gunicorn"]["path_get"], path_post="/" + CONFIG["connection_webserver_gunicorn"]["path_post"], path_root=PATH + "/" + CONFIG["connection_webserver_gunicorn"]["path_root"], path_tmp=PATH + "/" + CONFIG["connection_webserver_gunicorn"]["path_tmp"], headers=CONFIG["connection_webserver_gunicorn"]["headers"], options=CONFIG["connection_webserver_gunicorn"]["options"], auth=CONFIG["connection_webserver_gunicorn"].getboolean("auth"), redirect=CONFIG["connection_webserver_gunicorn"].getboolean("redirect"), path_redirect_root=CONFIG["connection_webserver_gunicorn"]["path_redirect_root"], path_redirect_not_found=CONFIG["connection_webserver_gunicorn"]["path_redirect_not_found"], max_content_lenght=CONFIG.getint("connection_webserver_gunicorn", "max_content_lenght"))
            webserver.register_auth_callback(process_auth)
            webserver.register_get_callback(process_get)
            webserver.register_post_callback(process_post)
            webserver.register_download_callback(process_download)
            webserver.register_upload_callback(process_upload)
            webserver.register_upload_auth_callback(process_upload_auth)
            webserver.start()




#### Start ####
def main():
    try:
        description = NAME + " - " + DESCRIPTION
        parser = argparse.ArgumentParser(description=description)

        parser.add_argument("-p", "--path", action="store", type=str, default=None, help="Path to alternative config directory")
        parser.add_argument("-pl", "--path_log", action="store", type=str, default=None, help="Path to alternative log directory")
        parser.add_argument("-l", "--loglevel", action="store", type=int, default=LOG_LEVEL)
        parser.add_argument("-s", "--service", action="store_true", default=False, help="Running as a service and should log to file")

        parser.add_argument("-t", "--test", action="store_true", default=False, help="Test Mode (No changes to files and no execution of cmd/script.)")

        parser.add_argument("--clear", action="store_true", default=False, help="Delete all temporary files")
        parser.add_argument("--clearbackup", action="store_true", default=False, help="Delete backup files")
        parser.add_argument("--cleartest", action="store_true", default=False, help="Delete temporary test mode files")

        parser.add_argument("--defaultconfig", action="store_true", default=False, help="Reset the configuration to default")
        parser.add_argument("--exampleconfig", action="store_true", default=False, help="Print verbose configuration example to stdout and exit")

        parser.add_argument("--userget", action="store_true", default=False, help="User administration - List all users")
        parser.add_argument("--userdelete", action="store", type=str, default=None, help="User administration - Delete USER")
        parser.add_argument("--user", action="store", type=str, default=None, help="User administration - Edit/Add USER")
        parser.add_argument("--password", action="store", type=str, default=None, help="User administration - Set PASSWORD")

        parser.add_argument("--variablesget", action="store_true", default=False, help="Variables - List all system/user variables")

        params = parser.parse_args()

        setup(path=params.path, path_log=params.path_log, loglevel=params.loglevel, service=params.service, mode_test=params.test)
        setup_path()


        if params.clear:
            path = CONFIG["path"]["tmp"]
            shutil.rmtree(path)
            os.makedirs(path)
            path = CONFIG["path"]["mode_test"]
            shutil.rmtree(path)
            os.makedirs(path)
            exit()

        if params.clearbackup:
            path = CONFIG["path"]["backup"]
            shutil.rmtree(path)
            os.makedirs(path)
            exit()

        if params.cleartest:
            path = CONFIG["path"]["mode_test"]
            shutil.rmtree(path)
            os.makedirs(path)
            exit()

        if params.defaultconfig:
            config_default(file=PATH + "/config.cfg")
            config_auth_default(file=PATH + "/config_auth.cfg")
            exit()

        if params.exampleconfig:
            print("Config File: " + PATH + "/config.cfg")
            print("Content:")
            print(DEFAULT_CONFIG)
            exit()

        if params.userget:
            user_get(PATH + "/config_auth.cfg")

        if params.userdelete:
            user_delete(PATH + "/config_auth.cfg", params.userdelete)

        if params.user and params.password:
            user_set(PATH + "/config_auth.cfg", params.user, params.password)

        if CONFIG["main"].getboolean("default_config"):
            log("Exit!", LOG_WARNING)
            log("First start with the default config!", LOG_WARNING)
            log("You should probably edit the config file \"" + PATH + "/config.cfg\" to suit your needs and use-case!", LOG_WARNING)
            log("Then restart this program again!", LOG_WARNING)
            exit()

        if not CONFIG["main"].getboolean("enabled"):
            log("Disabled in config file. Exit!", LOG_INFO)
            exit()

        setup_variables()
        setup_log()
        build("setup", CONFIG["main"]["lng"])

        if params.variablesget:
            if VARIABLES:
                print("")
                print("...............................................................................")
                print("Available variables for webinterface or config replace:")
                for key in VARIABLES:
                    print("")
                    print("#### " + key + " ####")
                    if VARIABLES[key]:
                        print(VARIABLES[key])
            if VARIABLES_SOFTWARE:
                print("")
                print("...............................................................................")
                print("require_software:")
                for key in VARIABLES_SOFTWARE["software"]:
                    print(key)
            print("")
            print("...............................................................................")
            print("require_system:")
            print(VARIABLES_SYSTEM.data["require"])
            print("")
            print("...............................................................................")
            print("require_user:")
            print(VARIABLES_USER.data["require"])
            exit()

        setup_connection()


    except KeyboardInterrupt:
        print("Terminated by CTRL-C")
        exit()


##############################################################################################################
# Files


#### Default configuration override file ####
DEFAULT_CONFIG_OVERRIDE = '''# This is the user configuration file to override the default configuration file.
# All settings made here have precedence.
# This file can be used to clearly summarize all settings that deviate from the default.
# This also has the advantage that all changed settings can be kept when updating the program.
'''


#### Default configuration file ####
DEFAULT_CONFIG = '''# This is the default config file.
# You should probably edit it to suit your needs and use-case.


#### Version ####

[version]
date = 2022-08-01 00:00:00
number = 0.0.1
name = ConfigInterfaceTool
description = Easy, minimalistic and simple interface for device/application administration and configuration.
note = 
author = 




#### Main ####

[main]
enabled = True
name = ConfigInterfaceTool
description = Easy, minimalistic and simple interface for device/application administration and configuration.

# Default language when automatic detection is disabled.
lng = en

# Automatically detect language.
lng_auto = True

# Default interface mode
mode_interface = basic #basic/advanced/expert

# Default data mode
mode_data = False #True=All / False=Used

# Test mode
mode_test = False




#### Path ####

[path]
# Backup files.
backup = backup

# Config cache files.
config = cache

# Config/Interface definitions.
config_files = config_files

# Config templates/files which are used for processing/execution.
config_templates = config_templates

# Software cache files.
software = cache

# Software definitions.
software_files = software_files

# Software templates/files which are used for processing/execution.
software_templates = software_templates

# Wizard cache files.
wizard = cache

# Wizard definitions.
wizard_files = wizard_files

# Wizard templates/files which are used for processing/execution.
wizard_templates = wizard_templates

tmp = tmp
mode_test = test
terminal = /tmp
auth_external = /var/www/configinterfacetool.htpasswd




#### Build ####
[build]
setup = variables_system;variables_user;software;variables_system_add;merge
config = variables_system;variables_user;variables_system_add;merge;interface;config;data;data_read;data_read_file
config_user = variables_system;variables_user;software;variables_system_add;merge;interface;config;data;data_read;data_read_file
data = merge
data_user = merge




#### Build add ####
[build_add]
system = version
user = 




#### Config ####

[config]
enabled = True
extension = cfg
extension_lng = lng
extension_template = 
extension_archive = tar
extension_transfer = tar
backup_auto = True
backup_auto_files = True
backup_auto_files_restore = True
backup_auto_files_exclude_type = log,log_file,log_cmd
backup_auto_name = _auto_backup
backup_auto_time_format = Y-m-d_H-M-S
backup_auto_max = 50
backup_user = True
backup_user_files = True
backup_user_files_restore = True
backup_user_files_exclude_type = log,log_file,log_cmd
backup_user_name = _user_backup
backup_factory = True
backup_factory_name = factory_backup
backup_factory_files_restore = True
backup_require_acknowledge = False
backup_require_reboot = False
backup_require_reload = False
system_sections = version;main;global;files;files_type;files_permission;files_owner
files_type = text #auto/text = Source -> Destination (Replace)  |  auto/env/ini/json/keyagr/keyval/toml/xml/yaml/raw = Source -> Destination (Edit)  |  auto/env/ini/json/keyagr/keyval/toml/xml/yaml/raw_edit = Destination -> Destination (Edit)  |  log/log_file/log_cmd = Read log
delimiter_lng=#
delimiter_variable=**
delimiter_variable_cmd=**
delimiter_variable_raw=####
delimiter_if_standard=####
delimiter_if_regex=####
delimiter_sections=*


[config_process]
require = True
require_acknowledge = True
require_reboot = True
require_reload = True
require_mode = True
require_software = True
require_system = True
require_user = True

files = True
files_create_path = True
files_create_file = True
files_permission = True
files_owner = True

execute = True
cmd = True
script = True

error_ignore = True

internal = False

value_replace = True
value_regex = True
value_regex_match = True
value_convert = True

value_cmd = True
value_script = True

variable = True
variable_cmd = True
variable_cleanup = False

if_standard = True
if_standard_cleanup = True
if_standard_cleanup_type = comment #delete/comment
if_standard_cleanup_value=#

if_regex = False
if_regex_cleanup = False
if_regex_cleanup_type = comment #delete/comment
if_regex_cleanup_value=#

variables_session = True
variables_system = True
variables_user = True
variables_data = True

variables_session_prefix = session_
variables_system_prefix = sys_
variables_user_prefix = usr_
#variables_data_prefix = 

variables_regex = True
variables_regex_search = [^a-zA-Z0-9-_]
variables_regex_replace = 

auto_read = True
auto_write = True
auto_add = True
auto_raw = True
env_read = True
env_write = True
env_add = True
env_raw = True
ini_read = True
ini_write = True
ini_add = True
ini_raw = True
json_read = True
json_write = True
json_add = True
json_raw = True
keyarg_read = True
keyarg_write = True
keyarg_add = True
keyarg_raw = True
keyval_read = True
keyval_write = True
keyval_add = True
keyval_raw = True
text_read = True
text_write = True
text_add = True
text_raw = True
toml_read = True
toml_write = True
toml_add = True
toml_raw = True
xml_read = True
xml_write = True
xml_add = True
xml_raw = True
yaml_read = True
yaml_write = True
yaml_add = True
yaml_raw = True
raw_read = True
raw_write = True
raw_add = True
raw_raw = True




[config_interface]




#### Software ####

[software]
enabled = True
extension = cfg
extension_lng = lng
extension_template = sh
system_sections = version;main;execute;files_lng;cmd;script;package;python
delimiter_variable=**


[software_process]
require = True
require_acknowledge = True
require_reboot = True
require_reload = True
require_mode = True
require_system = True
require_user = True

cmd = True
script = True
fallback = False
package = True
python = True

status = True
install = True
uninstall = True
update = True

cmd_status_cmd_before = 
cmd_status_cmd_after = 
cmd_install_cmd_before = 
cmd_install_cmd_after = 
cmd_uninstall_cmd_before = 
cmd_uninstall_cmd_after = 
cmd_update_cmd_before = 
cmd_update_cmd_after = 

script_status_cmd_before = 
script_status_cmd_after = 
script_install_cmd_before = 
script_install_cmd_after = 
script_uninstall_cmd_before = 
script_uninstall_cmd_after = 
script_update_cmd_before = 
script_update_cmd_after = 

package_status_cmd = 
package_status_cmd_before = 
package_status_cmd_after = 
package_install_cmd = apt install
package_install_cmd_before = apt update
package_install_cmd_after = 
package_uninstall_cmd = apt remove
package_uninstall_cmd_before = 
package_uninstall_cmd_after = 
package_update_cmd = 
package_update_cmd_before = 
package_update_cmd_after = 

python_status_cmd = 
python_status_cmd_before = 
python_status_cmd_after = 
python_install_cmd = pip3 install
python_install_cmd_before = 
python_install_cmd_after = 
python_uninstall_cmd = pip3 uninstall
python_uninstall_cmd_before = 
python_uninstall_cmd_after = 
python_update_cmd = pip3 --upgrade
python_update_cmd_before = 
python_update_cmd_after = 


[software_interface]




#### Wizard ####

[wizard]
enabled = True
extension = cfg
extension_lng = lng
extension_template = sh
system_sections = version;main;execute;files_lng;output;output_replace;output_replace*;output_regex;output_regex*;input;input_replace;input_replace*;input_regex;input_regex*
delimiter_variable=**


[wizard_process]
require = True
require_acknowledge = True
require_reboot = True
require_reboot_now = True
require_reload = True
require_mode = True
require_software = True
require_system = True
require_user = True

group = True
cmd = True
cmd_reboot = sleep 5 && shutdown -r now &
script = True
fallback = True
next = True

output = True
output_group = True

output_replace_cmd = True
output_replace_color = False
output_replace_ansi = True
output_replace_log = True
output_replace_whitespace = True
output_replace_double_lines = True
output_replace_special_characters = True
output_replace_unnecessary_characters = True
output_replace_lng = True

output_color = 30=black;31=red;32=green;33=yellow;34=blue;35=purple;36=cyan

output_state = True
output_state_regex = .*@.*# $

output_append = True
output_append_regex = ^(?!\\r)

output_replace = True
output_regex = True

input_replace_whitespace = False

input_replace = True
input_regex = True

input_generate_mode = raw #raw/ansi/replace
input_generate_force = False
input_generate_default = True
input_generate = True

log_mode = replace #raw/replace
log_output = True
log_input = True
log_input_initial = False
log_state = True
log_expert_output = True
log_expert_output_terminal = False
log_expert_output_max_lenght = 0 #0=unlimited
log_expert_output_max_lines = 50 #0=unlimited

system_load = True
history = True

terminal_cmd = bash
terminal_cmd_args = 
terminal_env = COLUMNS=1
terminal_timeout = 0
terminal_read_bytes = 20
terminal_size_rows = 100
terminal_size_cols = 200
terminal_restart_session = False


[wizard_interface]
# Button labels.
button_input = Next
button_input-de = Weiter
button_enter = Next
button_enter-de = Weiter
button_yes = Yes
button_yes-de = Ja
button_no = No
button_no-de = Nein
button_cancel = Cancel
button_cancel-de = Abbrechen
button_abort = Abort
button_abort-de = Abbrechen
button_abort_group = Abort all
button_abort_group-de = Alle Abbrechen
button_next = Next
button_next-de = Weiter
button_skip = Skip
button_skip-de = Überspringen
button_start = Start
button_start-de = Start
button_restart_abort = Restart
button_restart_abort-de = Neustart
button_restart_success = Restart
button_restart_success-de = Neustart
button_restart_error = Restart
button_restart_error-de = Neustart
button_reboot = Reboot
button_reboot-de = Neustart

# Message labels.
message_abort = Do you really want to cancel the wizard?
message_abort-de = Möchten Sie den Assistenten wirklich abbrechen?
message_abort_group = Do you really want to cancel all wizards?
message_abort_group-de = Möchten Sie alle Assistenten wirklich abbrechen?
message_restart_abort = Do you really want to restart the wizard?
message_restart_abort-de = Möchten Sie den Assistenten wirklich neu starten?
message_restart_success = Do you really want to restart the wizard?
message_restart_success-de = Möchten Sie den Assistenten wirklich neu starten?
message_restart_error = Do you really want to restart the wizard?
message_restart_error-de = Möchten Sie den Assistenten wirklich neu starten?
message_reboot = Perform a restart? The wizard will then continue automatically.
message_reboot-de = Neustart durchführen? Anschließend wird der Assistent automatisch fortgesetzt.

# Output labels.
output_reboot = To continue, it is mandatory to restart the system. To do this, click on "Restart". Then the wizard will continue automatically. If this does not work, please reload the page. The restart will take a moment.
output_reboot-de = Zum Fortfahren muss das System zwingend neu gestartet werden. Klicken Sie hierzu auf "Neustart". Anschließend wird der Assistent automatisch fortgesetzt. Sollte dies nicht funktionieren, dann laden Sie bitte die Seite neu. Der Neustart wird einen Moment dauern.

# Labels of the log messages.
log_enter = Next
log_enter-de = Weiter

log_abort = Aborted!
log_abort-de = Abgebrochen!
log_error = Finished with errors!
log_error-de = Beendet mit Fehlern!
log_finish = Finished!
log_finish-de = Beendet!

# Classes of the log messages.
class_abort = bg-yellow
class_error = bg-red
class_finish = bg-green




#### Connections ####
[connection]
enabled = True


# Webserver - aiohttp
[connection_webserver_aiohttp]
enabled = False
auth = True
redirect = True
host = 0.0.0.0
port = 8080
path_root = www
path_get = index
path_post = index
path_redirect_root = index.html
path_redirect_not_found = 
path_tmp = tmp
headers = Access-Control-Allow-Origin=*
options = 
max_content_lenght = 16 #MB


# Webserver - flask
[connection_webserver_flask]
enabled = False
auth = True
redirect = True
host = 0.0.0.0
port = 8080
path_root = www
path_get = index
path_post = index
path_redirect_root = index.html
path_redirect_not_found = 
path_tmp = tmp
headers = Access-Control-Allow-Origin=*
options = 
max_content_lenght = 16 #MB


# Webserver - gunicorn
[connection_webserver_gunicorn]
enabled = True
auth = True
redirect = True
host = 0.0.0.0
port = 8080
path_root = www
path_get = index
path_post = index
path_redirect_root = index.html
path_redirect_not_found = 
path_tmp = tmp
headers = Access-Control-Allow-Origin=*
options = workers=1;threads=1;timeout=120
max_content_lenght = 16 #MB


# Websocket
[connection_websocket]
enabled = False


# Reticulum
[connection_reticulum]
enabled = False




#### Interface ####

[interface_process]
content = True
config = True
software = True
wizard = True

name_section = True
data_section = False

lng = True
lng_delimiter = -


[interface_main]
window = Config Interface
header = Config Interface
class = 
class_menu = !m-resp
class_container = 
style = 
icon = 

delimiter_1 = ;
delimiter_2 = ,
delimiter_val = =

get_timeout = 60 #Seconds
get_size_url = 4094 #Characters
get_size_header = 4094 #Characters
get_all = True
post_timeout = 20 #Seconds
post_upload_timeout = 30 #Seconds
reconnect_delay = 5 #Seconds
reconnect_timeout = 60 #Seconds
reload_delay = 60 #Seconds
ping = False
ping_delay = 10 #Seconds
ping_timeout = 30 #Seconds
toast_timeout = 3 #Seconds
toasts_timeout = 5 #Seconds

mode_screen = False
slide_tab = True
slide_tab_area_ratio = 0.12
slide_menu = True
slide_menu_up = True
slide_menu_area_ratio = 0.12
slide_menu_area_size = 40
scroll_page = True
scroll_tab = True
save_view = True
save_data = True
submit_empty = False
submit_global = True

msg_btn = False
msg_btn_error = True
msg_btn_confirm = False
msg_file_mode = Please specify the IP address of the device!;File mode
msg_file_mode-de = Bitte die IP Adresse des Gerätes angeben!;Datei Modus
msg_error = -;Error
msg_error-de = -;Fehler
msg_error_val = Data transmission faulty!;Error
msg_error_val-de = Datenübertragung fehlerhaft!;Fehler
msg_error_con = Connection failed!;Error
msg_error_con-de = Verbindung fehlgeschlagen!;Fehler
msg_error_empty = No data to send!;Error
msg_error_empty-de = Keine Daten zum senden!;Fehler
msg_error_upload = Upload failed!;Error
msg_error_upload-de = Upload fehlgeschlagen!;Fehler
msg_con = Connect, please wait...;Info
msg_con-de = Verbinde, bitte warten...;Info
msg_con_error = Connection failed! Reconnect in seconds:;Error
msg_con_error-de = Verbindung fehlgeschlagen! Neu verbinden in Sekunden:;Fehler
msg_con_timeout = Connection failed! Maximum number of attempts reached!;Error
msg_con_timeout-de = Verbindung fehlgeschlagen! Maximale Anzahl an Versuchen erreicht!;Fehler
msg_reconnect = Restart, please wait...;Info
msg_reconnect-de = Neustart, bitte warten...;Info
msg_cfg_load = Loading configuration, please wait...;Info
msg_cfg_load-de = Lade Konfiguration, bitte warten...;Info
msg_data_load = Loading data, please wait...;Info
msg_data_load-de = Lade Daten, bitte warten...;Info
msg_cfg_data_load = Loading configuration + data, please wait...;Info;
msg_cfg_data_load-de = Lade Konfiguration + Daten, bitte warten...;Info;


[interface_terminal_main]
window = Terminal
header = Terminal
class = 

menu_status_connecting = Connecting...
menu_status_connecting-de = Verbinde...
menu_status_connect = Connected
menu_status_connect-de = Verbunden
menu_status_disconnect = Disconnected
menu_status_disconnect-de = Getrennt
menu_reload = Reload
menu_reload-de = Neu laden
menu_exit = Exit/Close
menu_exit-de = Beenden/Schließen

msg_connect = Welcome! Press enter to start!
msg_connect-de = Willkommen! Drücken Sie zum Starten die Eingabetaste!
msg_disconnect = \\r\\n\\r\\nSession terminated!\\r\\nTo restart the session please reload the page!
msg_disconnect-de = \\r\\n\\r\\nDie Sitzung ist beendet!\\r\\nZum Neustart der Sitzung laden Sie bitte die Seite neu!


[interface_messages]
post_ok = 
post_ok-de = 
post_ok_execute = Saved successfully
post_ok_execute-de = Erfolgreich gespeichert
post_ok_cmd = 
post_ok_cmd-de = 
post_ok_script = 
post_ok_script-de = 
post_ok_upload = Upload successfully
post_ok_upload-de = Upload erfolgeich


[interface_default_values]
abort = Abort;OK
abort-de = Abbrechen;OK
abort_confirm = Abort;OK
abort_confirm-de = Abbrechen;OK
button = True
checkbox = False;True
checkboxslider = False;True
confirm = Abort;OK
confirm-de = Abbrechen;OK
nav = False=<;True=>
submit_confirm = Abort;OK
submit_confirm-de = Abbrechen;OK
switch = False=Off;True=On
toggle = False=Off;True=On
wizard = Prev;Next;Save
wizard-de = Zurück;Weiter;Speichern


[interface_default_icons]
abort = fas fa-circle-xmark;fas fa-circle-check
confirm = fas fa-circle-xmark;fas fa-circle-check
abort_confirm = fas fa-circle-xmark;fas fa-circle-check
submit_confirm = fas fa-circle-xmark;fas fa-circle-check


[interface_default_messages]


[interface_default_caption_required]
* = This field is required!
*-de = Dieses Feld ist Erforderlich!


[interface_default_caption_pattern]
* = The value is invalid!
*-de = Der Wert ist ungültig!
password = The value does not meet the requirements!
password-de = Der Wert entspricht nicht den Anforderungen!
password_verfiy = The value does not meet the requirements!
password_verfiy-de = Der Wert entspricht nicht den Anforderungen!


[interface_types_name]
abort
abort_confirm
button
buttongroup
checkbox
checkboxslider
bool
color
colorpalette
colorpicker
colorslider
confirm
date
editor
editor_code
email
file
hidden
live
month
nav
number
numberslider
password
passwordverify
radio
radiogroup
range
search
select
selectbutton
selectlist
slider
status
submit
submit_confirm
switch
table
tel
text
textbutton
textarea
time
toggle
url
week
wizard
wizard_start


[interface_types_data]
value
value_html
value_icon
value_progress
value_txt


[interface_types_label]
button
buttongroup
card
card_start
cardgroup
cardgroup_start
checkbox
checkboxslider
bool
color
colorpalette
colorpicker
colorslider
date
editor
editor_code
email
fieldset
fieldset_start
fieldsetgroup
fieldsetgroup_start
file
label
month
nav
number
numberslider
password
passwordverify
progress
radio
radiogroup
range
search
select
selectbutton
selectlist
slider
status
switch
tabgroup
tabgroup_start
table
tel
text
textbutton
textarea
time
url
value
value_html
value_icon
value_progress
value_txt
week
wizard
wizard_start


[interface_mapping]
type = t
name = n
value_name = n
label = l
label_header = l_h
header_label = l_h
labels = ls
label_icon = i
label_red = l_r
label_green = l_g
label_blue = l_b
caption = ca
description = ca
icon = i
icon_header = i_h
header_icon = i_h
icons = is
icons_default = id
image = i
images = is
data = d
value_data = d
data_update = u
value_data_update = u
data_mode = m
value_data_mode = m
update = u
value = v
value_type = vt
value_view = vv
value_0_disabled = v_0_di
value_1_disabled = v_1_di
value_false_disabled = v_0_di
value_true_disabled = v_1_di
value_0_view = v_0_v
value_1_view = v_1_v
value_false_view = v_0_v
value_true_view = v_1_v
value_view_toggle = v_v
content = c
content_icon = c_i
content_header = c_h
content_footer = c_f
cmd = cmd
cmd_success = cmd_s
cmd_error = cmd_e
disabled = di
value_required = r
value_required_caption = r_ca
required = r
required_caption = r_ca
state = st
class = cl
class_0 = cl_0
class_1 = cl_1
class_false = cl_0
class_true = cl_1
class_header = cl_h
header_class = cl_h
class_content = cl_c
content_class = cl_c
class_footer = cl_f
footer_class = cl_f
style = s
style_0 = s_0
style_1 = s_1
style_false = s_0
style_true = s_1
align = al
alignment = al
orientation = al
width = wi
height = he
minlenght = min
maxlenght = max
min = min
max = max
step = step
value_regex_match = pa
value_regex_match_caption = pa_ca
pattern = pa
pattern_caption = pa_ca
placeholder = ph
mode = m
multiple = mu
values = vs
values_default = vd
options = vs
rows = rows
cols = cols
count = co
message = msg
messages = msgs
message_icons = is
msg = msg
msgs = msgs
msg_icons = is
window = w
header = h
prev = prev
next = next
get = get
data_get = get
set = set
data_set = get
post = set
data_post = set
tabindex = ti
transmit = tx
transmit_empty = txe
tx = tx
tx_empty = txe
send = tx
send_empty = txe
submit = tx
submit_empty = txe
main = main
active = a
opened = a
target = w
destination = de
autocomplete = ac
autofocus = af
spellcheck = sc
error_ignore = e
space = sp

default_values = vd
default_icons = id
default_messages = msgsd
default_caption_required = r_cad
default_caption_pattern = pa_cad


[interface_mapping_type]


[interface_mapping_page]
page_* = *


[interface_mapping_tab]
tab_* = *


[interface_mapping_page_name]
header = c_header
header_fix = c_header_fix
footer = c_footer
footer_fix = c_footer_fix


[interface_mapping_tab_name]
header = c_header
header_fix = c_header_fix
footer = c_footer
footer_fix = c_footer_fix
'''




DEFAULT_CONFIG_AUTH = '''
[user]
#any
admin=$6$O2nSzkoi1MAfzlPc$/FxL6L//8/OV0hvnP8.xrEpavwgzqzlnAfN82goExuWFeAUJLpZS/LzJ1gI5hCioBg4reI/aSm/18.o59omA.0
'''


##############################################################################################################
# Init


if __name__ == "__main__":
    main()