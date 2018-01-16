#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2012-2018 The Wazo Authors  (see the AUTHORS file)
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

import sys, psutil
from munin import MuninPlugin
"""
" http://github.com/samuel/python-munin
"""


class XivoAsteriskMem(MuninPlugin):
    args = '--base 1024 -l 0'
    title = 'XiVO Asterisk mem'
    vlabel = 'Bytes'
    scaled = False
    category = 'xivo'

    @property
    def fields(self):
        return [('ast_mem_res', dict(
                    label = 'ast_mem_res',
                    info = 'Asterisk resident memory consumption',
                    type = 'GAUGE',
                    draw = 'AREA',
                    min = '0')),
                ('ast_mem_virt', dict(
                    label = 'ast_mem_virt',
                    info = 'Asterisk virtual memory consumption',
                    type = 'GAUGE',
                    draw = 'LINE2',
                    min = '0'))]

    def execute(self):
        ast_pid = 0
        proc_name = 'asterisk'
        for proc in psutil.process_iter():
            if proc_name == proc.name():
                ast_pid = proc.pid
                break

        if ast_pid == 0:
            print 'ast_mem_res.value 0'
            print 'ast_mem_virt.value 0'
            sys.exit(1)

        handler = psutil.Process(ast_pid)
        asterisk_memory = handler.memory_info()

        print 'ast_mem_res.value %s' % str(asterisk_memory.rss)
        print 'ast_mem_virt.value %s' % str(asterisk_memory.vms)


if __name__ == "__main__":
    XivoAsteriskMem().run()
