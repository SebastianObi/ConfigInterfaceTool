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
import os
import time

#### Terminal ####
import subprocess
import pty
import termios
import select
import struct
import fcntl
import shlex
import signal


##############################################################################################################
# Class


class terminal_class:
    fd = None
    pid = None


    def size(self, rows, cols, xpix=0, ypix=0):
        if self.fd:
            size = struct.pack("HHHH", rows, cols, xpix, ypix)
            fcntl.ioctl(self.fd, termios.TIOCSWINSZ, size)


    def get(self, timeout=None, read_bytes=None):
        if not timeout:
            timeout = self.timeout
        if not read_bytes:
            read_bytes = self.read_bytes
        if not self.fd: return ["", 0]
        (data_ready, _, _) = select.select([self.fd], [], [], timeout)
        if not data_ready: return ["", 0]
        output = ""
        state = 0
        try:
            read_bytes = 1024 * read_bytes
            output = os.read(self.fd, read_bytes).decode()
        except Exception as e:
            output = str(e)
            state = e.errno
            if e.errno == 5: self.stop()
        return [output, state]


    def set(self, cmd):
        if not self.fd and not self.restart_session: return False
        if not self.fd and self.restart_session: self.start()
        if not self.fd: return False
        try:
            cmd = cmd.strip() + "\n"
            os.write(self.fd, cmd.encode())
        except:
            return False
        return True


    def set_env(self, env=None):
        if not env: return

        if "bash" in self.cmd:
            cmd = "export"
        elif "sh" in self.cmd:
            cmd = "setenv"
        else:
            cmd = ""

        if cmd != "":
            for key in env.keys():
                self.set(cmd + " " + key + "=" + env[key])
            time.sleep(1)
            self.get()


    def start(self):
        if not self.pid:
            (pid, fd) = pty.fork()
            if pid == 0:
                cmd = [self.cmd] + shlex.split(self.cmd_args)
                if self.path != "": os.chdir(self.path)
                subprocess.run(cmd)
            else:
                self.fd = fd
                self.pid = pid
                self.size(self.fd, self.rows, self.cols)
            self.set_env(self.env)


    def stop(self):
        if self.fd:
            fd = self.fd
            self.fd = None
            self.pid = None
            try:
                os.kill(fd, signal.SIGTERM)
            except:
                return False
        return True


    def __init__(self, path="", cmd="bash", cmd_args="", env=None, timeout=0, read_bytes=20, rows=100, cols=200, restart_session=True):
        self.path = path
        self.cmd = cmd
        self.cmd_args = cmd_args
        self.env = env
        self.timeout = timeout
        self.read_bytes = read_bytes
        self.rows = rows
        self.cols = cols
        self.restart_session = restart_session
        self.start()
        return


    def __del__(self):
        self.stop()
        return
