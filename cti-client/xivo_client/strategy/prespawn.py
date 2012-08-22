# -*- coding: UTF-8 -*-

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

from gevent import sleep


class NullPreSpawnStrategy(object):

    def pre_spawn(self):
        pass


class TimedPreSpawnStrategy(object):

    def __init__(self, wait_time_strategy):
        self._time_strategy = wait_time_strategy

    def pre_spawn(self):
        wait_time = self._time_strategy.get_time()
        sleep(wait_time)


class BurstPreSpawnStrategy(object):

    def __init__(self, burst, wait_time):
        self._burst = burst
        self._wait_time = wait_time
        self._n = 0

    def pre_spawn(self):
        new_n = self._n + 1
        if new_n >= self._burst:
            self._n = 0
            sleep(self._wait_time)
        else:
            self._n = new_n
