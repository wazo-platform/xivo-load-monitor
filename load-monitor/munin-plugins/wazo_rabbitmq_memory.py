#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from __future__ import print_function

import psutil

from munin import MuninPlugin
"""
" http://github.com/samuel/python-munin
"""


class WazoRabbitMQMemory(MuninPlugin):
    args = '--base 1024 -l 0'
    title = 'RabbitMQ memory'
    vlabel = 'Bytes'
    scaled = False
    category = 'xivo'

    @property
    def fields(self):
        return [
            ('rabbitmq_mem_res', {
                'label': 'rabbitmq_mem_res',
                'info': 'RabbitMQ resident memory consumption',
                'type': 'GAUGE',
                'draw': 'AREA',
                'min': '0'
            }),
            ('rabbitmq_mem_virt', {
                'label': 'rabbitmq_mem_virt',
                'info': 'RabbitMQ virtual memory consumption',
                'type': 'GAUGE',
                'draw': 'LINE2',
                'min': '0'
            })
        ]

    def execute(self):
        rabbitmq_mem_res, rabbitmq_mem_virt = 0, 0
        rabbitmq_procs = (proc for proc in psutil.process_iter()
                          if proc.name() == 'beam.smp' and proc.username() == 'rabbitmq')
        for proc in rabbitmq_procs:
            mem = proc.memory_info()
            rabbitmq_mem_res, rabbitmq_mem_virt = mem.rss, mem.vms

        print('rabbitmq_mem_res.value', rabbitmq_mem_res)
        print('rabbitmq_mem_virt.value', rabbitmq_mem_virt)


if __name__ == "__main__":
    WazoRabbitMQMemory().run()
