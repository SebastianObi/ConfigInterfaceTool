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


#### Encryption ####
import crypt


##############################################################################################################
# Class


class convert_class:


    def size_to_human_readable(self, size, decimal_places=3, source="B"):
        size = int(size)
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


    def network_mask_to_cidr(self, mask):
        if mask == "": return ""
        try:
            return str(sum([str(bin(int(octet))).count("1") for octet in mask.split(".")]))
        except:
            None
        return ""


    def network_cidr_to_mask(self, cidr):
        if cidr == "": return ""
        try:
            cidr = int(cidr)
            if cidr < 0 or cidr > 32: return ""
            mask = (0xffffffff >> (32 - cidr)) << (32 - cidr)
            return (str( (0xff000000 & mask) >> 24)   + '.' +
                    str( (0x00ff0000 & mask) >> 16)   + '.' +
                    str( (0x0000ff00 & mask) >> 8)    + '.' +
                    str( (0x000000ff & mask)))
        except:
            None
        return ""


    def string_to_bool(self, val):
        if val == "on" or val == "On" or val == "true" or val == "True" or val == "yes" or val == "Yes" or val == "1" or val == "open" or val == "opened" or val == "up":
            return "1"
        elif val == "off" or val == "Off" or val == "false" or val == "False" or val == "no" or val == "No" or val == "0" or val == "close" or val == "closed" or val == "down":
            return "0"
        elif val != "":
            return "1"
        else:
            return "0"


    def htpasswd(self, val):
        return crypt.crypt(val)


    def run(self, config, value):
        if config == "" or value == "":
            return value

        try:
            if config == "size_to_human_readable":
                return self.size_to_human_readable(value)
            elif config == "network_mask_to_cidr":
                return self.network_mask_to_cidr(value)
            elif config == "network_cidr_to_mask":
                return self.network_cidr_to_mask(value)
            elif config == "string_to_bool":
                return self.string_to_bool(value)
            elif config == "htpasswd" or config == "md5" or config == "crypt":
                return self.htpasswd(value)
        except:
            None

        return value


    def __init__(self):
        return


    def __del__(self):
        return
