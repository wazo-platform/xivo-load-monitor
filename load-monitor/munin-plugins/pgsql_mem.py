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


class PgsqlMem(MuninPlugin):
    args = '--base 1024 -l 0'
    title = 'Pgsql mem'
    vlabel = 'Bytes'
    scaled = False
    category = 'postgresql'

    @property
    def fields(self):
        return [('pg_mem_res', dict(
                    label = 'pg_mem_res',
                    info = 'Postgresql resident memory consumption',
                    type = 'GAUGE',
                    draw = 'AREA',
                    min = '0')),
                ('pg_mem_virt', dict(
                    label = 'pg_mem_virt',
                    info = 'Postgresql virtual memory consumption',
                    type = 'GAUGE',
                    draw = 'LINE2',
                    min = '0'))]

    def execute(self):
        pg_processes = [process for process in psutil.process_iter() if process.name() == 'postgres']

        pg_mem_res = sum([process.memory_info().rss for process in pg_processes])
        pg_mem_virt = sum([process.memory_info().vms for process in pg_processes])

        print 'pg_mem_res.value %s' % str(pg_mem_res)
        print 'pg_mem_virt.value %s' % str(pg_mem_virt)


if __name__ == "__main__":
    PgsqlMem().run()
