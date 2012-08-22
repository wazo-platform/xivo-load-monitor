# -*- coding: UTF-8 -*-

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
