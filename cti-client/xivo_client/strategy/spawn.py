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

from gevent.pool import Group, Pool


class GroupSpawnStrategy(object):

    def __init__(self):
        self._group = Group()

    def spawn(self, scenario):
        self._group.spawn(scenario.run)

    def post_run(self):
        self._group.join()


class PoolSpawnStrategy(object):

    def __init__(self, limit):
        self._pool = Pool(limit)

    def spawn(self, scenario):
        self._pool.spawn(scenario.run)

    def post_run(self):
        self._pool.join()
