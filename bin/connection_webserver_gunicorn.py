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


#### Webserver ####
# Install: pip3 install gunicorn
# Source: 
import gunicorn.app.base

#### Webserver ####
# Install: pip3 install flask
# Source: 
from flask import Flask, send_from_directory, request, redirect, Response, send_file

#### Webserver Basic Auth ####
# Install: pip3 install flask_httpauth
# Source: 
from flask_httpauth import HTTPBasicAuth

#### Filename ####
import os
import re
import unicodedata


##############################################################################################################
# Class


class connection_webserver_gunicorn_app_class(gunicorn.app.base.BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()


    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)


    def load(self):
        return self.application


##############################################################################################################
# Class


class connection_webserver_gunicorn_class:
    auth_callback = None
    get_callback = None
    post_callback = None
    download_callback = None
    upload_callback = None
    upload_auth_callback = None

    auth = None
    app = None
    auth_handler = HTTPBasicAuth()


    def filename_secure(self, filename):
        filename = unicodedata.normalize("NFKD", filename)
        filename = filename.encode("ascii", "ignore").decode("ascii")
        filename_ascii_strip_re = re.compile(r"[^A-Za-z0-9_.-]")
        for sep in os.path.sep, os.path.altsep:
            if sep:
                filename = filename.replace(sep, " ")
        filename = str(filename_ascii_strip_re.sub("", "_".join(filename.split()))).strip("._")
        return filename


    def handle_auth(self, username, password):
        if self.auth:
           if self.auth_callback is not None:
               if self.auth_callback(username, password):
                   return username
        else:
            return username
        return False


    @auth_handler.login_required
    def handle_files(self, filename):
        return send_from_directory(self.path_root, filename)


    @auth_handler.login_required
    def handle_root(self):
        return send_from_directory(self.path_root, self.path_redirect_root)


    @auth_handler.login_required
    def handle_get(self):
        receive = request.args.get("json")
        if not receive:
            receive = request.headers.get('json')
            if not receive:
                 receive = ""

        if request.args.get("file"):
            if self.download_callback is not None:
                file, filename = self.download_callback(receive)
                if file != "":
                    try:
                        return send_file(file, attachment_filename=filename)
                    except Exception as e:
                        return str(e)

        if self.get_callback is not None:
            response = Response(self.get_callback(receive))
        else:
            response = Response("")

        return self.handle_headers(response)


    @auth_handler.login_required
    def handle_post(self):
        receive = request.form.get("json")
        if not receive: receive = ""
        response = None

        if "file" in request.files:
            file = request.files["file"]
            if file.filename == "": return self.handle_headers(Response(""))
            if self.upload_auth_callback is not None:
                if not self.upload_auth_callback(file.filename): return self.handle_headers(Response(""))
            if self.upload_callback is not None and self.path_tmp:
                filename = self.path_tmp + "/" + self.filename_secure(file.filename)
                file.save(filename)
                response = Response(self.upload_callback(receive, filename))

        if response is None:
            if self.post_callback is not None:
                response = Response(self.post_callback(receive))
            else:
                response = Response("")

        return self.handle_headers(response)


    def handle_headers(self, response):
        for key in self.headers:
            response.headers[key] = self.headers[key]
        return response


    def handle_not_found(self, test):
        return redirect(self.path_redirect_not_found, code=302)


    def register_auth_callback(self, handler_function):
        if self.auth:
            self.auth_callback = handler_function


    def register_get_callback(self, handler_function):
        self.get_callback = handler_function


    def register_post_callback(self, handler_function):
        self.post_callback = handler_function


    def register_download_callback(self, handler_function):
        self.download_callback = handler_function

    def register_upload_callback(self, handler_function):
        self.upload_callback = handler_function


    def register_upload_auth_callback(self, handler_function):
        self.upload_auth_callback = handler_function


    def start(self):
        connection_webserver_gunicorn_app_class(self.app, self.options).run()


    def stop(self):
        return


    def __init__(self, host, port, path_get, path_post, path_root, path_tmp=None, headers="", options="", auth=False, redirect=False, path_redirect_root="", path_redirect_not_found="", max_content_lenght=16):
        self.host = host
        self.port = port
        self.auth = auth
        self.redirect = redirect
        self.path_get = path_get
        self.path_post = path_post
        self.path_root = path_root
        self.path_tmp = path_tmp
        self.path_redirect_root = path_redirect_root
        self.path_redirect_not_found = path_redirect_not_found
        self.max_content_lenght = max_content_lenght * 1000 * 1000

        self.headers = {}
        if headers != "":
            headers = headers.split(";")
            for val in headers:
                val = val.split("=")
                if len(val) == 2:
                    self.headers[val[0]] = val[1]

        self.options = {'bind': '%s:%s' % (self.host, self.port)}
        if options != "":
            options = options.split(";")
            for val in options:
                val = val.split("=")
                if len(val) == 2:
                    self.options[val[0]] = val[1]

        self.app = Flask(__name__)
        self.app.config['MAX_CONTENT_LENGTH'] = self.max_content_lenght

        self.auth_handler.verify_password(self.handle_auth)

        if self.redirect and self.path_redirect_not_found != "":
            self.app.register_error_handler(404, self.handle_not_found)

        self.app.add_url_rule(self.path_get, 'get', self.handle_get, methods=["GET"])
        self.app.add_url_rule(self.path_post, 'post', self.handle_post, methods=["POST"])
        self.app.add_url_rule('/<path:filename>', 'files', self.handle_files)
        if self.redirect and self.path_redirect_root != "":
            self.app.add_url_rule('/', 'root', self.handle_root)


    def __del__(self):
        return