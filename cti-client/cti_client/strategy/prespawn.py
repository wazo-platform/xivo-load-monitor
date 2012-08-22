# -*- coding: UTF-8 -*-

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
