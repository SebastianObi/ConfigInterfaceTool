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

#### System Sensors ####
# Install: pip3 install psutil
import psutil


##############################################################################################################
# Class


class variables_system_class:
    config = None
    data = defaultdict(dict)
    prefix = ""


    def convert_size_to_human_readable(self, size, decimal_places=3, source="B"):
        units = ['B','KB','MB','GB','TB']
        units_search = ['B','KB','MB','GB','TB']

        for x in units_search:
            if x.lower() == source.lower():
                break
            units.remove(x)

        for unit in units:
            if size < 1024.0:
                break
            size /= 1024.0

        return f"{size:.{decimal_places}f}{unit}"


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


    def build_config(self):
        key = "config"
        self.data["config_"+key] = ""
        files = sorted(glob.glob(self.config["path"][key+"_files"] + "/*" + self.config[key]["extension"], recursive=False))
        for filename in files:
            try:
                file = configparser.ConfigParser(allow_no_value=True, inline_comment_prefixes="#")
                file.sections()
                file.read(filename, encoding='utf-8')
                row = []
                row.append(os.path.basename(filename))
                if file.has_section("version"):
                    if file.has_option("version", "number"):
                        row.append(file["version"]["number"])
                    else:
                        row.append("")
                    if file.has_option("version", "date"):
                        row.append(re.sub(r'\s+(?:[01]\d|2[0-3]):(?:[0-5]\d):(?:[0-5]\d)', '', file["version"]["date"]))
                    else:
                        row.append("")
                    if file.has_option("version", "name"):
                        row.append(file["version"]["name"])
                    else:
                        row.append("")
                    if file.has_option("version", "author"):
                        row.append(file["version"]["author"])
                    else:
                        row.append("")
                else:
                    row.append("")
                    row.append("")
                    row.append("")
                    row.append("")
                self.data["config_"+key] = self.data["config_"+key] + "<tr><td>" + "</td><td>".join(row) + "</td></tr>"
            except:
                continue

        key = "software"
        self.data["config_"+key] = ""
        files = sorted(glob.glob(self.config["path"][key+"_files"] + "/*" + self.config[key]["extension"], recursive=False))
        for filename in files:
            try:
                file = configparser.ConfigParser(allow_no_value=True, inline_comment_prefixes="#")
                file.sections()
                file.read(filename, encoding='utf-8')
                row = []
                row.append(os.path.basename(filename))
                if file.has_section("version"):
                    if file.has_option("version", "number"):
                        row.append(file["version"]["number"])
                    else:
                        row.append("")
                    if file.has_option("version", "date"):
                        row.append(re.sub(r'\s+(?:[01]\d|2[0-3]):(?:[0-5]\d):(?:[0-5]\d)', '', file["version"]["date"]))
                    else:
                        row.append("")
                    if file.has_option("version", "name"):
                        row.append(file["version"]["name"])
                    else:
                        row.append("")
                    if file.has_option("version", "author"):
                        row.append(file["version"]["author"])
                    else:
                        row.append("")
                else:
                    row.append("")
                    row.append("")
                    row.append("")
                    row.append("")
                self.data["config_"+key] = self.data["config_"+key] + "<tr><td>" + "</td><td>".join(row) + "</td></tr>"
            except:
                continue

        key = "wizard"
        self.data["config_"+key] = ""
        files = sorted(glob.glob(self.config["path"][key+"_files"] + "/*" + self.config[key]["extension"], recursive=False))
        for filename in files:
            try:
                file = configparser.ConfigParser(allow_no_value=True, inline_comment_prefixes="#")
                file.sections()
                file.read(filename, encoding='utf-8')
                row = []
                row.append(os.path.basename(filename))
                if file.has_section("version"):
                    if file.has_option("version", "number"):
                        row.append(file["version"]["number"])
                    else:
                        row.append("")
                    if file.has_option("version", "date"):
                        row.append(re.sub(r'\s+(?:[01]\d|2[0-3]):(?:[0-5]\d):(?:[0-5]\d)', '', file["version"]["date"]))
                    else:
                        row.append("")
                    if file.has_option("version", "name"):
                        row.append(file["version"]["name"])
                    else:
                        row.append("")
                    if file.has_option("version", "author"):
                        row.append(file["version"]["author"])
                    else:
                        row.append("")
                else:
                    row.append("")
                    row.append("")
                    row.append("")
                    row.append("")
                self.data["config_"+key] = self.data["config_"+key] + "<tr><td>" + "</td><td>".join(row) + "</td></tr>"
            except:
                continue


    def build_system(self):
        self.data["platform"] = platform.system()
        self.data["release"] = platform.release()

        self.data["model"] = ""
        result = self.file("/proc/cpuinfo")
        if result != "":
            if group := re.search(r'Model\s+:\s+(.*)', result):
                self.data["model"] = group.group(1)
            else:
                result = self.file("/proc/device-tree/model")
                if result != "":
                    self.data["model"] = result

        self.data["release_name"] = self.cmd("lsb_release -sd")
        self.data["hostname"] = self.cmd("hostname -f")


    def build_os_release_raw(self):
        self.data["os_release_raw"] = self.cmd("cat /etc/os-release")


    def build_interface_eth(self):
        interface = []
        result = self.cmd("ls /sys/class/net | grep -v lo")
        if result != "":
            regex = re.findall(r'(\w+)', result)
            for match in regex:
                interface.append(match)
        self.data["interface_eth"] = ";".join(interface)


    def build_interface_wifi(self):
        interface = []
        self.data["interface_wifi_raw"] = ""
        result = self.cmd("iw dev")
        if result != "":
            self.data["interface_wifi_raw"] = result
            result = result + "\n"
            regex = re.findall(r'Interface\s(.*)\n', result)
            for match in regex:
                interface.append(match)
        self.data["interface_wifi"] = ";".join(interface)
        self.data["interface_wifi_raw"] = self.data["interface_wifi_raw"] + self.cmd("iwconfig")


    def build_interface_wifi_networks(self):
        interface = []
        result = self.cmd("for i in $(ls /sys/class/net/ | egrep -v ^lo$); do sudo iw dev $i scan | grep SSID | awk '{print substr($0, index($0,$2)) }'; done 2>/dev/null | sort -u")
        if result != "":
            result = result + "\n"
            regex = re.findall(r'(.*)\n', result)
            for match in regex:
                if match != "SSID List":
                    interface.append(match)
        self.data["interface_wifi_networks"] = ";".join(interface)


    def build_interface_wifi_networks_connected(self):
        interface = []
        result = self.cmd("iwconfig")
        if result != "":
            regex = re.findall(r'ESSID:\"([^"]+)\"', result)
            for match in regex:
                interface.append(match)
        self.data["interface_wifi_networks_connected"] = ";".join(interface)


    def build_interface_usb(self):
        interface = []
        self.data["interface_usb_raw"] = ""
        result = self.cmd("lsusb")
        if result != "":
            self.data["interface_usb_raw"] = result
            result = result + "\n"
            regex = re.findall(r'(.*)\n', result)
            for match in regex:
                interface.append(match)
        self.data["interface_usb"] = ";".join(interface)


    def build_interface_bluetooth(self):
        interface = []
        self.data["interface_bluetooth_raw"] = ""
        result = self.cmd("ls /sys/class/bluetooth/")
        if result != "":
            self.data["interface_bluetooth_raw"] = result
            regex = re.findall(r'(\w+)', result)
            for match in regex:
                interface.append(match)
        self.data["interface_bluetooth"] = ";".join(interface)


    def build_interface_serial(self):
        interface = []
        self.data["interface_serial_raw"] = ""
        result = self.cmd("ls /dev/ | grep 'ttyACM\|ttyUSB'")
        if result != "":
            self.data["interface_serial_raw"] = self.data["interface_serial_raw"] + result
            result = result + "\n"
            regex = re.findall(r'(.*)\n', result)
            for match in regex:
                interface.append(match)
        result = self.cmd("ls /dev/serial/by-id/")
        if result != "":
            self.data["interface_serial_raw"] = self.data["interface_serial_raw"] + result
            result = result + "\n"
            regex = re.findall(r'(.*)\n', result)
            for match in regex:
                interface.append("/dev/serial/by-id/" + match)
        self.data["interface_serial"] = ";".join(interface)


    def build_interface_snd(self):
        interface = []
        self.data["interface_snd_raw"] = ""
        result = self.cmd("ls /dev/snd")
        if result != "":
            self.data["interface_snd_raw"] = self.data["interface_snd_raw"] + result
            result = result + "\n"
            regex = re.findall(r'(.*)\n', result)
            for match in regex:
                interface.append(match)
        self.data["interface_snd"] = ";".join(interface)


    def build_interface_cat(self):
        interface = []
        self.data["interface_cat_raw"] = ""
        result = self.cmd("ls /dev/ | grep 'ttyUSB'")
        if result != "":
            self.data["interface_cat_raw"] = self.data["interface_cat_raw"] + result
            result = result + "\n"
            regex = re.findall(r'(.*)\n', result)
            for match in regex:
                interface.append(match)
        self.data["interface_cat"] = ";".join(interface)


    def build_cpu(self):
        self.data["cpu_count"] = self.cmd("nproc --all")


    def build_memory(self):
        self.data["memory"] = str(round(psutil.virtual_memory().percent))
        self.data["swap"] = str(round(psutil.swap_memory().percent))

        result = self.cmd("free -m")
        if result != "":
            if group := re.search(r'^Mem:\s+(\d+)\s+(\d+)\s+(\d+).*', result, flags=re.M):
                self.data["memory_total_int"] = group[1]
                self.data["memory_total"] = self.convert_size_to_human_readable(int(group[1]), 3, "MB")
                self.data["memory_used_int"] = group[2]
                self.data["memory_used"] = self.convert_size_to_human_readable(int(group[2]), 3, "MB")
                self.data["memory_free_int"] = group[3]
                self.data["memory_free"] = self.convert_size_to_human_readable(int(group[3]), 3, "MB")
                if group[1] == "0" or group[2] == "0":
                    self.data["memory_used_percent"] = "0"
                else:
                    self.data["memory_used_percent"] = str(round(int(group[2])/int(group[1])*100, 2))
            if group := re.search(r'^Swap:\s+(\d+)\s+(\d+)\s+(\d+)', result, flags=re.M):
                self.data["swap_total_int"] = group[1]
                self.data["swap_total"] = self.convert_size_to_human_readable(int(group[1]), 3, "MB")
                self.data["swap_used_int"] = group[2]
                self.data["swap_used"] = self.convert_size_to_human_readable(int(group[2]), 3, "MB")
                self.data["swap_free_int"] = group[3]
                self.data["swap_free"] = self.convert_size_to_human_readable(int(group[3]), 3, "MB")
                if group[1] == "0" or group[2] == "0":
                    self.data["swap_used_percent"] = "0"
                else:
                    self.data["swap_used_percent"] = str(round(int(group[2])/int(group[1])*100, 2))


    def build_load(self):
        self.data["cpu"] = str(round(psutil.cpu_percent()))

        result = self.cmd("awk '{print $1}' /proc/loadavg")
        if result != "":
            self.data["load"] = result.replace("\n", "")
            self.data["load_percent"] = str(float(self.data["load"])*100/int(self.data["cpu_count"]))


    def build_temp(self):
        result = self.cmd("cat /sys/class/thermal/thermal_zone0/temp")
        if result != "":
            self.data["temp"] = str(int(result)/1000) + "°C" 


    def build_date_time(self):
        self.data["date_time"] = self.cmd("date +'%Y-%m-%d %T'")


    def build_date(self):
        self.data["date"] = self.cmd("date +'%Y-%m-%d'")


    def build_time(self):
        self.data["time"] = self.cmd("date +'%T'")


    def build_uptime(self):
        self.data["starttime"] = self.cmd("uptime -s")
        self.data["uptime"] = self.cmd("uptime -p").replace("up ", "")


    def build_network_interface_raw(self):
        self.data["network_interface_raw"] = self.cmd("ifconfig")


    def build_network_route_raw(self):
        self.data["network_route_raw"] = self.cmd("ip route list")


    def build_network_route_default(self):
        interface = []
        self.data["network_route_default"] = ""
        self.data["network_connection_gw"] = "False"
        self.data["network_connection_online_ip"] = "False"
        self.data["network_connection_online_dns"] = "False"
        result = self.cmd("ip route list")
        if result != "":
            result = result + "\n"
            regex = re.findall(r'default via (([0-9]{1,3}\.){3}[0-9]{1,3}) dev (\w*)', result)
            for match in regex:
                self.data["network_route_default"] = match[2] + " " + match[0]
                append = match[2] + " " + match[0]
                result_dns = self.cmd('host ' + match[0] + ' | sed -rn "s/.*domain name pointer (.*)\./\1/p" | head -n 1')
                if result_dns != "":
                    append = append + " (" + result_dns + ")"
                result_connection = self.cmd('ping -W1 -c 1 -I ' + match[2] + ' ' + match[0] +' |  sed -rn "s/.*icmp_seq=1.*time=.*/OK/p"')
                if result_connection!= "":
                    append = append + " (Connection GW: " + result_connection + ")"
                    self.data["network_connection_gw"] = "True"
                result_connection = self.cmd('ping -W1 -c 1 -I ' + match[2] + ' 8.8.8.8 |  sed -rn "s/.*icmp_seq=1.*time=.*/OK/p"')
                if result_connection!= "":
                    append = append + " (Connection IP: " + result_connection + ")"
                    self.data["network_connection_online_ip"] = "True"
                result_connection = self.cmd('ping -W1 -c 1 -I ' + match[2] + ' google.de |  sed -rn "s/.*icmp_seq=1.*time=.*/OK/p"')
                if result_connection!= "":
                    append = append + " (Connection DNS: " + result_connection + ")"
                    self.data["network_connection_online_dns"] = "True"
                interface.append(append)
        self.data["network_route_default_raw"] = "\n".join(interface)


    def build_disk(self):
        self.data["disk"] = str(round(psutil.disk_usage('/').percent))


    def build_disk_raw(self):
        self.data["disk_raw"] = self.cmd("lsblk -f -m -o NAME,FSTYPE,LABEL,SIZE,FSAVAIL,FSUSE%,MOUNTPOINT | grep -v loop")


    def build_mount_raw(self):
        self.data["mount_raw"] = self.cmd("df -h")


    def build_software_reticulum_raw(self):
        self.data["software_reticulum_raw"] = self.cmd("rnsd --version") + "\n\n" + self.cmd("rnstatus")


    def build_software_nomadnet_raw(self):
        self.data["software_nomadnet_raw"] = self.cmd("nomadnet --version")


    def build(self):
        self.data = defaultdict(dict)

        self.build_config()
        self.build_system()
        self.build_os_release_raw()
        self.build_interface_eth()
        self.build_interface_wifi()
        #self.build_interface_wifi_networks() # Disabled because it leads to problems with active access point
        #self.build_interface_wifi_networks_connected # Disabled because it leads to problems with active access point
        self.build_interface_usb()
        self.build_interface_bluetooth()
        self.build_interface_serial()
        self.build_interface_snd()
        self.build_interface_cat()
        self.build_cpu()
        self.build_memory()
        self.build_load()
        self.build_temp()
        self.build_date_time()
        self.build_date()
        self.build_time()
        self.build_uptime()
        self.build_network_interface_raw()
        self.build_network_route_raw()
        self.build_network_route_default()
        self.build_disk()
        self.build_disk_raw()
        self.build_mount_raw()

        self.build_software_reticulum_raw()
        self.build_software_nomadnet_raw()

        self.data["require"] = "model:" + self.data["model"] + " - platform:" + self.data["platform"] + " - release:" + self.data["release"]
        self.data["require"] = self.data["require"].lower()

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

        if self.prefix + "config" in receive_json["data"]: self.build_config()
        if self.prefix + "system" in receive_json["data"]: self.build_system()
        if self.prefix + "os_release_raw" in receive_json["data"]: self.build_os_release_raw()
        if self.prefix + "interface_eth" in receive_json["data"]: self.build_interface_eth()
        if self.prefix + "interface_wifi" in receive_json["data"] or self.prefix + "interface_wifi_raw" in receive_json["data"]: self.build_interface_wifi()
        #if self.prefix + "interface_wifi_networks" in receive_json["data"]: self.build_interface_wifi_networks() # Disabled because it leads to problems with active access point
        #if self.prefix + "interface_wifi_networks_connected" in receive_json["data"]: self.build_interface_wifi_networks_connected() # Disabled because it leads to problems with active access point
        if self.prefix + "interface_usb" in receive_json["data"] or self.prefix + "interface_usb_raw" in receive_json["data"]: self.build_interface_usb()
        if self.prefix + "interface_bluetooth" in receive_json["data"] or self.prefix + "interface_bluetooth_raw" in receive_json["data"]: self.build_interface_bluetooth()
        if self.prefix + "interface_serial" in receive_json["data"] or self.prefix + "interface_serial_raw" in receive_json["data"]: self.build_interface_serial()
        if self.prefix + "interface_snd" in receive_json["data"] or self.prefix + "interface_snd_raw" in receive_json["data"]: self.build_interface_snd()
        if self.prefix + "interface_cat" in receive_json["data"] or self.prefix + "interface_cat_raw" in receive_json["data"]: self.build_interface_cat()
        if self.prefix + "cpu" in receive_json["data"]: self.build_cpu()
        if self.prefix + "memory" in receive_json["data"]: self.build_memory()
        if self.prefix + "load" in receive_json["data"]: self.build_load()
        if self.prefix + "temp" in receive_json["data"]: self.build_temp()
        if self.prefix + "date_time" in receive_json["data"]: self.build_date_time()
        if self.prefix + "date" in receive_json["data"]: self.build_date()
        if self.prefix + "time" in receive_json["data"]: self.build_time()
        if self.prefix + "uptime" in receive_json["data"]: self.build_uptime()
        if self.prefix + "network_interface_raw" in receive_json["data"]: self.build_network_interface_raw()
        if self.prefix + "network_route_raw" in receive_json["data"]: self.build_network_route_raw()
        if self.prefix + "network_route_default" in receive_json["data"] or self.prefix + "network_route_default_raw" in receive_json["data"] or self.prefix + "network_connection_gw" in receive_json["data"] or self.prefix + "network_connection_online_ip" in receive_json["data"] or self.prefix + "network_connection_online_dns" in receive_json["data"]: self.build_network_route_default()
        if self.prefix + "disk" in receive_json["data"]: self.build_disk()
        if self.prefix + "disk_raw" in receive_json["data"]: self.build_disk_raw()
        if self.prefix + "mount_raw" in receive_json["data"]: self.build_mount_raw()

        if self.prefix + "software_reticulum_raw" in receive_json["data"]: self.build_software_reticulum_raw()
        if self.prefix + "software_nomadnet_raw" in receive_json["data"]: self.build_software_nomadnet_raw()

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
