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


##############################################################################################################
# Class


class connection_reticulum_class:
    auth_callback = None
    get_callback = None
    post_callback = None


    def register_auth_callback(self, handler_function):
        if self.auth:
            self.auth.register_callback(handler_function)


    def register_get_callback(self, handler_function):
        self.get_callback = handler_function


    def register_post_callback(self, handler_function):
        self.post_callback = handler_function


    def start(self):
        return


    def stop(self):
        return


    def __init__(self, port, path_get, path_post, path_root, auth=False, redirect=False, path_redirect=None):
        self.port = port
        self.auth = auth
        self.redirect = redirect
        self.path_get = path_get
        self.path_post = path_post
        self.path_root = path_root
        self.path_redirect = path_redirect


    def __del__(self):
        return