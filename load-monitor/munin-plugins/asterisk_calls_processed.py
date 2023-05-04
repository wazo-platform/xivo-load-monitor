#!/usr/bin/env python3
# Copyright 2012-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
from telnetlib import Telnet

from pymunin import MuninPlugin, MuninGraph, muninMain


def init_socket(host: str, username: str, password: str) -> Telnet:
    timeout = 2
    port = 5038
    tn = Telnet()

    tn.open(host, port, timeout)
    tn.read_until(b"Asterisk Call Manager")
    tn.write(b"Action: login\r\n")
    tn.write(f"Username: {username}\r\n".encode())
    tn.write(f"Secret: {password}\r\n".encode())
    tn.write(b"Events: off\r\n")
    tn.write(b"\r\n")
    return tn


def validate_connection(tn: Telnet) -> None:
    accepted = tn.read_until(b"Authentication accepted", 2)
    if not (accepted.find(b'Authentication accepted') >= 0):
        print('ERROR : Authentication not accepted')
        sys.exit(1)


def get_data(tn: Telnet, command: str) -> bytes:
    tn.write(b"Action: command\r\n")
    tn.write(f"Command: {command}\r\n".encode())
    tn.write(b"\r\n")
    data = tn.read_until(b"calls processed")
    return data


def process_data(data: bytes) -> float:
    last_line = data.split(b'\n')[-1]
    if last_line.startswith(b'Output: '):
        last_line = last_line[len('Output: '):]
    return int(last_line.split(b' ')[0]) / 2


class XivoCtidSocket(MuninPlugin):
    plugin_name = 'asterisk_calls_processed'
    _category = 'xivo'
    _graph_name = 'asteriskcalls'
    _field_name = _graph_name
    _info = 'Number of calls processed by asterisk since last restart'

    def __init__(self, argv=(), env=None, debug=False):
        super().__init__(argv, env, debug)

        if self.graphEnabled(self._graph_name):
            graph = MuninGraph(
                'Asterisk calls processed',
                self._category,
                vlabel='Nb of Calls',
                info=self._info,
            )
            graph.addField(
                self._field_name,
                'Calls processed since last restart',
                type='GAUGE',
                draw='AREA',
                min='0',
                info=self._info,
            )
            self.appendGraph(self._graph_name, graph)

    def retrieveVals(self):
        if self.hasGraph(self._graph_name):
            host = '127.0.0.1'
            username = 'xivo_munin_user'
            password = 'jeSwupAd0'
            command = 'core show channels'

            tn = init_socket(host, username, password)
            validate_connection(tn)
            data = get_data(tn, command)
            tn.close()
            results = process_data(data)

            self.setGraphVal(self._graph_name, self._field_name, results)

    def autoconf(self) -> bool:
        return True


if __name__ == "__main__":
    sys.exit(muninMain(XivoCtidSocket))
