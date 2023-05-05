#!/usr/bin/env python3
# Copyright 2012-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import psutil
from pymunin import MuninPlugin, MuninGraph, muninMain


FIELD_MEM_RES = 'ast_mem_res'
FIELD_MEM_VIRT = 'ast_mem_virt'


class XivoAsteriskMem(MuninPlugin):
    """
    Xivo Asterisk Memory plugin for Munin

    https://github.com/munin-monitoring/PyMunin3
    """
    plugin_name = 'xivo_asterisk_mem'
    _category = 'xivo'
    _graph_name = 'asterisk_mem'

    def __init__(self, argv=(), env=None, debug=False):
        super().__init__(argv, env, debug)

        if self.graphEnabled(self._graph_name):
            graph = MuninGraph(
                'XiVO Asterisk mem',
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
                info='Asterisk resident memory consumption'
            )
            graph.addField(
                FIELD_MEM_VIRT,
                FIELD_MEM_VIRT,
                type='GAUGE',
                draw='LINE2',
                min='0',
                info='Asterisk virtual memory consumption'
            )
            self.appendGraph(self._graph_name, graph)

    def retrieveVals(self):
        if self.hasGraph(self._graph_name):
            ast_pid = 0
            proc_name = 'asterisk'
            for proc in psutil.process_iter():
                if proc_name == proc.name():
                    ast_pid = proc.pid
                    break

            if ast_pid == 0:
                self.setGraphVal(self._graph_name, FIELD_MEM_RES, 0)
                self.setGraphVal(self._graph_name, FIELD_MEM_VIRT, 0)
                sys.exit(1)

            handler = psutil.Process(ast_pid)
            asterisk_memory = handler.memory_info()

            self.setGraphVal(self._graph_name, FIELD_MEM_RES, asterisk_memory.rss)
            self.setGraphVal(self._graph_name, FIELD_MEM_VIRT, asterisk_memory.vms)

    def autoconf(self) -> bool:
        return True


if __name__ == "__main__":
    sys.exit(muninMain(XivoAsteriskMem))
