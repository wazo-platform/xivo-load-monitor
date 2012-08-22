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

import random


class ConstantTimeStrategy(object):

    def __init__(self, wait_time):
        self._wait_time = wait_time

    def get_time(self):
        return self._wait_time


class RandomTimeStrategy(object):

    def __init__(self, min_, max_):
        self._min = min_
        self._max = max_

    def get_time(self):
        return random.uniform(self._min, self._max)
