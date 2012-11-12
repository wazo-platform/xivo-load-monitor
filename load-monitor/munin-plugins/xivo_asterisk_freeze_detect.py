#!/usr/bin/python

# Copyright (C) 2012  Avencall
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

# Need sipsak package
# Need an Asterisk account

import sys
import socket
import os
import time

from munin import MuninPlugin
"""
" http://github.com/samuel/python-munin
"""

class XivoAsteriskFreezeDetect(MuninPlugin):
    title = 'Xivo Asterisk freeze detect'
    vlabel = 'Boolean'
    scaled = False
    category = 'xivo'

    @property
    def fields(self):
        return [('asterisk_freeze_detect', dict(
                label = 'asterisk_freeze_detect',
                info = 'Detection of Asterisk freeze',
                type = 'GAUGE',
                draw = 'AREA',
                min = '0',
                max = '1'))]

    def _sipsak_check(self, host, account):
        command = '/usr/bin/sipsak -s sip:%s@%s 2> /dev/null' % (account, host)
        status = os.system(command)
        if status > 0:
            time.sleep(1)
            status2 = os.system(command)
            if status2 > 0:
                return 1
        else:
            return 0

    def execute(self):

        host = '10.38.1.1'
        account = '1051'

        try:
            exit_status = self._sipsak_check(host, account)
            if exit_status == 0:
                asterisk_freeze_detect = 1
            else:
                asterisk_freeze_detect = 0
        except:
            asterisk_freeze_detect = 0

        print 'asterisk_freeze_detect.value %s' % str(asterisk_freeze_detect)

if __name__ == "__main__":
    XivoAsteriskFreezeDetect().run()

