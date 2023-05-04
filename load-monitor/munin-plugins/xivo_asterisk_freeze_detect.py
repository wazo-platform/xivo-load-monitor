#!/usr/bin/env python3
# Copyright 2012-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

# Need sipsak package
# Need an Asterisk account

import sys
import os
import time

from pymunin import MuninPlugin, MuninGraph, muninMain


class XivoAsteriskFreezeDetect(MuninPlugin):
    """
    Xivo Asterisk Freeze Detection plugin for Munin

    https://github.com/munin-monitoring/PyMunin3
    """

    plugin_name = 'xivo_asterisk_freeze_detect'
    _category = 'xivo'
    _graph_name = 'asterisk_freeze_detect'
    _field_name = _graph_name
    _info = 'Detection of Asterisk freeze'

    def __init__(self, argv=(), env=None, debug=False):
        super().__init__(argv, env, debug)

        if self.graphEnabled(self._graph_name):
            graph = MuninGraph(
                'Xivo Asterisk freeze detect',
                self._category,
                vlabel='Boolean',
                info=self._info,
            )
            graph.addField(
                self._field_name,
                'asterisk_freeze_detect',
                type='GAUGE',
                draw='AREA',
                min='0',
                max='1',
                info=self._info,
            )
            self.appendGraph(self._graph_name, graph)

    def _sipsak_check(self, host: str, account: str) -> int:
        command = f'/usr/bin/sipsak -s sip:{account}@{host} 2> /dev/null'
        status = os.system(command)
        if status > 0:
            time.sleep(1)
            status2 = os.system(command)
            if status2 > 0:
                return 1
        else:
            return 0

    def retrieveVals(self) -> None:
        if self.hasGraph(self._graph_name):
            host = '127.0.0.1'
            account = '1000'

            try:
                exit_status = self._sipsak_check(host, account)
                if exit_status == 0:
                    asterisk_freeze_detect = 1
                else:
                    asterisk_freeze_detect = 0
            except Exception:
                asterisk_freeze_detect = 0

            self.setGraphVal(self._graph_name, self._field_name, asterisk_freeze_detect)

    def autoconf(self) -> bool:
        return True


if __name__ == "__main__":
    sys.exit(muninMain(XivoAsteriskFreezeDetect))
