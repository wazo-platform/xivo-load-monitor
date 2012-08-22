# -*- coding: UTF-8 -*-

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
