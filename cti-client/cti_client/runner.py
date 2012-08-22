# -*- coding: UTF-8 -*-

import logging

logger = logging.getLogger(__name__)


class ScenarioRunner(object):

    def __init__(self, scenarios, spawn_strategy, pre_spawn_strategy):
        self._scenarios = scenarios
        self._spawn_strategy = spawn_strategy
        self._pre_spawn_strategy = pre_spawn_strategy

    def run(self):
        for scenario in self._scenarios:
            self._pre_spawn_strategy.pre_spawn()
            logger.info('Spawning scenario %s...', scenario)
            self._spawn_strategy.spawn(scenario)
        self._spawn_strategy.post_run()
