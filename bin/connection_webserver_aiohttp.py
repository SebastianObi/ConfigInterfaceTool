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
# Install: pip3 install aiohttp
# Source: https://github.com/aio-libs/aiohttp
from aiohttp import web

#### Webserver Basic Auth ####
# Install: pip3 install aiohttp_basicauth
# Source: https://github.com/romis2012/aiohttp-basicauth
from aiohttp_basicauth import BasicAuthMiddleware

#### Filename ####
import os
import re
import unicodedata


##############################################################################################################
# Class


class connection_webserver_aiohttp_auth_class(BasicAuthMiddleware):
    callback = None


    def register_callback(self, handler_function):
        self.callback = handler_function


    async def check_credentials(self, username, password, request):
        if self.callback is not None:
            return self.callback(username, password)
        else:
            return False


##############################################################################################################
# Class


class connection_webserver_aiohttp_class:
    auth_callback = None
    get_callback = None
    post_callback = None
    download_callback = None
    upload_callback = None
    upload_auth_callback = None

    auth = None
    app = None


    def filename_secure(self, filename):
        filename = unicodedata.normalize("NFKD", filename)
        filename = filename.encode("ascii", "ignore").decode("ascii")
        filename_ascii_strip_re = re.compile(r"[^A-Za-z0-9_.-]")
        for sep in os.path.sep, os.path.altsep:
            if sep:
                filename = filename.replace(sep, " ")
        filename = str(filename_ascii_strip_re.sub("", "_".join(filename.split()))).strip("._")
        return filename


    async def handle_root(self, request):
        return web.FileResponse(path=self.path_root + "/" + self.path_redirect_root, status=200) 


    async def handle_get(self, request):
        receive = request.rel_url.query.get("json", "")
        if receive == "":
            receive = request.headers.get("json", "")

        file = request.rel_url.query.get("file", None)

        if file is not None:
            if self.download_callback is not None:
                file, filename = self.download_callback(receive)
                if file != "":
                    try:
                        headers = {}
                        headers["Content-Disposition"] = "attachment; filename=" + filename
                        return web.FileResponse(file, headers = headers)
                    except Exception as e:
                        return web.Response(text=str(e))

        if self.get_callback is not None:
            return web.Response(text=self.get_callback(receive))
        else:
            return web.Response(text="")


    async def handle_post(self, request):
        data = await request.post()
        if "json" in data:
            receive = data["json"]
        else:
            receive = ""
        response = None

        if "file" in data:
            file = data["file"]
            if file.filename == '': return web.Response(text="")
            if self.upload_auth_callback is not None:
                if not self.upload_auth_callback(file.filename): return web.Response(text="")
            if self.upload_callback is not None and self.path_tmp:
                filename = self.path_tmp + "/" + self.filename_secure(file.filename)
                with open(filename, 'wb') as f:
                    f.write(file.file.read())
                    response = self.upload_callback(receive, filename)

        if response is None:
            if self.post_callback is not None:
                response = self.post_callback(receive)
            else:
                response = ""

        return web.Response(text=response)


    async def handle_headers(self, request, response):
        for key in self.headers:
            response.headers[key] = self.headers[key]


    @web.middleware
    async def error_middleware(self, request, handler):
        try:
            response = await handler(request)
            if response.status != 404:
                return response
        except web.HTTPException as ex:
            if ex.status != 403 and ex.status != 404:
                raise
        return web.HTTPFound(self.path_redirect_not_found)


    def register_auth_callback(self, handler_function):
        if self.auth:
            self.auth.register_callback(handler_function)


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
        web.run_app(self.app, port=self.port)


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

        self.options = {}
        if options != "":
            options = options.split(";")
            for val in options:
                val = val.split("=")
                if len(val) == 2:
                    self.options[val[0]] = val[1]

        self.app = web.Application()

        if self.auth:
            self.auth = connection_webserver_aiohttp_auth_class()
            self.app.middlewares.append(self.auth)

        if self.redirect and self.path_redirect_not_found != "":
            self.app.middlewares.append(self.error_middleware)

        self.app.add_routes([web.get(self.path_get, self.handle_get)])
        self.app.add_routes([web.post(self.path_post, self.handle_post)])
        if self.redirect and self.path_redirect_root != "":
            self.app.add_routes([web.get("/", self.handle_root)])
        self.app.add_routes([web.static("/", self.path_root, show_index=False, append_version=True)])
        self.app.on_response_prepare.append(self.handle_headers)


    def __del__(self):
        return