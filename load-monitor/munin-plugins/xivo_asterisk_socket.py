#!/usr/bin/env python3
# Copyright 2012-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import socket
import sys

from pymunin import MuninPlugin, MuninGraph, muninMain


class XivoAsteriskSocket(MuninPlugin):
    """
    Xivo Asterisk Socket plugin for Munin

    https://github.com/munin-monitoring/PyMunin3
    """
    plugin_name = 'xivo_asterisk_socket'
    _category = 'xivo'
    _graph_name = 'asterisk_socket'
    _field_name = _graph_name
    _info = 'Status of Asterisk socket'

    def __init__(self, argv=(), env=None, debug=False):
        super().__init__(argv, env, debug)

        if self.graphEnabled(self._graph_name):
            graph = MuninGraph(
                'Xivo Asterisk socket',
                self._category,
                vlabel='Boolean',
                info=self._info,
                scale=False,

            )
            graph.addField(
                self._field_name,
                'asterisk_socket_status',
                type='GAUGE',
                draw='AREA',
                min='0',
                max='1',
                info=self._info,
            )
            self.appendGraph(self._graph_name, graph)

    def retrieveVals(self):
        if self.hasGraph(self._graph_name):
            host = '127.0.0.1'
            port = 5038

            # UDP port by changing "socket.SOCK_STREAM" to "socket.SOCK_DGRAM"
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            try:
                s.connect((host, port))
                s.shutdown(2)
                asterisk_socket_status = 1
                """
                print "Success connecting to "
                print host + " on port: " + str(port)
                """
            except Exception:
                asterisk_socket_status = 0
                """
                print "Cannot connect to "
                print host + " on port: " + str(port)
                """
            self.setGraphVal(self._graph_name, self._field_name, asterisk_socket_status)

    def autoconf(self) -> bool:
        return True


if __name__ == "__main__":
    sys.exit(muninMain(XivoAsteriskSocket))
