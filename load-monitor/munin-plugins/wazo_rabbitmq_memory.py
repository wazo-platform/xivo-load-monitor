#!/usr/bin/env python3
# Copyright 2017-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import psutil

from pymunin import MuninPlugin, MuninGraph, muninMain


FIELD_MEM_RES = 'rabbitmq_mem_res'
FIELD_MEM_VIRT = 'rabbitmq_mem_virt'


class WazoRabbitMQMemory(MuninPlugin):
    """
    Xivo Asterisk Freeze Detection plugin for Munin

    https://github.com/munin-monitoring/PyMunin3
    """
    plugin_name = 'wazo_rabbitmq_memory'
    _category = 'xivo'
    _graph_name = 'wazo_rabbitmq_mem'

    def __init__(self, argv=(), env=None, debug=False):
        super().__init__(argv, env, debug)

        if self.graphEnabled(self._graph_name):
            graph = MuninGraph(
                'RabbitMQ memory',
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
                info='RabbitMQ resident memory consumption'
            )
            graph.addField(
                FIELD_MEM_VIRT,
                FIELD_MEM_VIRT,
                type='GAUGE',
                draw='LINE2',
                min='0',
                info='RabbitMQ virtual memory consumption'
            )
            self.appendGraph(self._graph_name, graph)

    def retrieveVals(self):
        if self.hasGraph(self._graph_name):
            rabbitmq_mem_res, rabbitmq_mem_virt = 0, 0
            rabbitmq_procs = (
                proc for proc in psutil.process_iter()
                if proc.name() == 'beam.smp' and proc.username() == 'rabbitmq'
            )
            for proc in rabbitmq_procs:
                mem = proc.memory_info()
                rabbitmq_mem_res, rabbitmq_mem_virt = mem.rss, mem.vms

            self.setGraphVal(self._graph_name, FIELD_MEM_RES, rabbitmq_mem_res)
            self.setGraphVal(self._graph_name, FIELD_MEM_VIRT, rabbitmq_mem_virt)

    def autoconf(self) -> bool:
        return True


if __name__ == "__main__":
    sys.exit(muninMain(WazoRabbitMQMemory))
