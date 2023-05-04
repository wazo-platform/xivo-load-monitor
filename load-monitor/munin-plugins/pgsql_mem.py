#!/usr/bin/env python3
# Copyright 2017-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import psutil

from pymunin import MuninPlugin, MuninGraph, muninMain


FIELD_MEM_RES = 'pg_mem_res'
FIELD_MEM_VIRT = 'pg_mem_virt'


class PgsqlMem(MuninPlugin):
    """
    Xivo Asterisk Freeze Detection plugin for Munin

    https://github.com/munin-monitoring/PyMunin3
    """
    plugin_name = 'pgsql_memory'
    _category = 'postgresql'
    _graph_name = 'pgsql_mem'

    def __init__(self, argv=(), env=None, debug=False):
        super().__init__(argv, env, debug)

        if self.graphEnabled(self._graph_name):
            graph = MuninGraph(
                'Pgsql memory',
                self._category,
                vlabel='Bytes',
                args='--base 1024 -l 0',
            )
            graph.addField(
                FIELD_MEM_RES,
                FIELD_MEM_RES,
                type='GAUGE',
                draw='AREA',
                min='0',
                info='Postgresql resident memory consumption'
            )
            graph.addField(
                FIELD_MEM_VIRT,
                FIELD_MEM_VIRT,
                type='GAUGE',
                draw='LINE2',
                min='0',
                info='Postgresql virtual memory consumption'
            )
            self.appendGraph(self._graph_name, graph)

    def retrieveVals(self):
        if self.hasGraph(self._graph_name):
            pg_processes = [
                process for process in psutil.process_iter()
                if process.name() == 'postgres'
            ]

            pg_mem_res = sum([process.memory_info().rss for process in pg_processes])
            pg_mem_virt = sum([process.memory_info().vms for process in pg_processes])

            self.setGraphVal(self._graph_name, FIELD_MEM_RES, pg_mem_res)
            self.setGraphVal(self._graph_name, FIELD_MEM_VIRT, pg_mem_virt)

    def autoconf(self) -> bool:
        return True


if __name__ == "__main__":
    sys.exit(muninMain(PgsqlMem))
