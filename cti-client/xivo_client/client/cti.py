# -*- coding: UTF-8 -*-

# Copyright (C) 2012  Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import logging
import json
from gevent import socket
from xivo_client.exception import AlreadyConnectedError, \
    RemoteConnectionClosedError

logger = logging.getLogger(__name__)


class CTIClient(object):

    DEFAULT_PORT = 5003
    DEFAULT_BUFSIZE = 4096

    def __init__(self, host, port=DEFAULT_PORT):
        self._host = host
        self._port = port
        self._sock = None
        self._buf = ''

    def connect(self):
        if self._sock is None:
            self._sock = self._new_socket()
        else:
            raise AlreadyConnectedError('already connected')

    def _new_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((self._host, self._port))
            return sock
        except Exception:
            try:
                raise
            finally:
                sock.close()

    def close(self):
        if self._sock is not None:
            self._sock.close()
            self._sock = None

    def recv(self, bufsize=DEFAULT_BUFSIZE):
        # warning: bypass buffer of recv_msg
        data = self._sock.recv(bufsize)
        if not data:
            raise RemoteConnectionClosedError()
        return data

    def recv_msg(self):
        buf = self._buf
        while True:
            head, sep, tail = buf.partition('\n')
            if sep:
                self._buf = tail
                return json.loads(head)
            else:
                buf += self.recv()

    def recv_msg_matching_class(self, msg_class):
        # warning: discard all other messages
        while True:
            msg = self.recv_msg()
            if msg['class'] == msg_class:
                return msg

    def send(self, data):
        return self._sock.send(data)

    def sendall(self, data):
        self._sock.sendall(data)

    def send_msg(self, msg):
        data = json.dumps(msg)
        self._sock.sendall(data + '\n')
