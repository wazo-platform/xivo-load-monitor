#!/usr/bin/env python3
# Copyright 2012-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import sqlite3
import sys

from pymunin import MuninPlugin, MuninGraph, muninMain


class XivoDiskSpace(MuninPlugin):
    """
    Xivo Disk Space plugin for Munin

    https://github.com/munin-monitoring/PyMunin3
    """
    plugin_name = 'xivo_disk_space_by_call_munin'
    _category = 'xivo'
    _graph_name = 'diskspacebycall'
    _field_name = _graph_name

    def __init__(self, argv=(), env=None, debug=False):
        super().__init__(argv, env, debug)

        if self.graphEnabled(self._graph_name):
            graph = MuninGraph(
                'Average disk space by call',
                self._category,
                vlabel='Bytes',
                info='Average space taken on disk for 1 call',
                args='--base 1024 -l 0',
            )
            graph.addField(
                self._field_name,
                'Average disk space by call',
                type='GAUGE',
                draw='AREA',
                min='0',
                info='Average space taken on disk for 1 call')
            self.appendGraph(self._graph_name, graph)

    def retrieveVals(self):
        if self.hasGraph(self._graph_name):
            db = '/tmp/diskspacebycall.db'
            table = 'tbl1'

            conn = sqlite3.connect(db)
            cursor = conn.cursor()
            cursor.execute(f'select * from {table}')
            results = cursor.fetchall()
            conn.close()

            if len(results) < 2:
                average = 0
            else:
                first_disk_avail = results[0][3]
                last_disk_avail = results[-1][3]
                first_call = results[0][2]
                last_call = results[-1][2]
                average = (first_disk_avail - last_disk_avail) / (last_call - first_call)

            self.setGraphVal(self._graph_name, self._field_name, average)

    def autoconf(self) -> bool:
        return True


if __name__ == "__main__":
    sys.exit(muninMain(XivoDiskSpace))
