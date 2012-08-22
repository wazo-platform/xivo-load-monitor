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

from xivo_client.client.step import StepRunner, LoginStep, \
    PasswordStep, LogoutStep, CapasStep, TimerStep, ConnectStep, \
    InitializationStep, IPBXListStep, SubscribeToQueuesStatsStep, SubscribeStep


class StandardScenario(object):

    _PRE_STEPS = [TimerStep('pre_connect'),
                  ConnectStep(),
                  TimerStep('post_connect'),
                  LoginStep(),
                  PasswordStep(),
                  TimerStep('post_password'),
                  CapasStep(),
                  IPBXListStep(),
                  SubscribeToQueuesStatsStep(),
                  SubscribeStep('meetme_update'),
                  InitializationStep(),
                  TimerStep('post_initialization')]
    _POST_STEPS = [LogoutStep()]

    def __init__(self, client, username, password, steps=None, stats=None):
        complete_steps = list(self._PRE_STEPS)
        if complete_steps:
            complete_steps.extend(steps)
        complete_steps.extend(self._POST_STEPS)
        if stats is None:
            stats = NoStatistics()
        self._stats = stats
        self._runner = StepRunner(client, complete_steps, {'username': username, 'password': password})

    def run(self):
        try:
            self._runner.run()
        finally:
            self._stats.post_run(self._runner)

    def print_infos(self):
        infos = self._runner.infos
        connect_time = infos['post_connect'] - infos['pre_connect']
        print 'Connection took %f s' % connect_time
        auth_time = infos['post_password'] - infos['post_connect']
        print 'Auth took %f s' % auth_time
        init_time = infos['post_initialization'] - infos['pre_connect']
        print 'Initialization took %f s' % init_time


class NoStatistics(object):

    def post_run(self, runner):
        pass


class StandardScenarioStatistics(object):

    def __init__(self):
        self.nb_tcp_connect = 0
        self.nb_tcp_success = 0
        self.nb_tcp_failed = 0
        self.nb_init_successful = 0
        self.min_init_time = None
        self.max_init_time = None

    def post_run(self, runner):
        infos = runner.infos
        self.nb_tcp_connect += 1
        if 'post_connect' in infos:
            self.nb_tcp_success += 1
        else:
            self.nb_tcp_failed += 1
        if 'post_initialization' in infos:
            self.nb_init_successful += 1
            init_time = infos['post_initialization'] - infos['pre_connect']
            if self.min_init_time is None:
                self.min_init_time = init_time
                self.max_init_time = init_time
            else:
                self.min_init_time = min(self.min_init_time, init_time)
                self.max_init_time = max(self.max_init_time, init_time)

    def print_stats(self):
        for name in ['nb_tcp_connect',
                     'nb_tcp_success',
                     'nb_tcp_failed',
                     'nb_init_successful',
                     'min_init_time',
                     'max_init_time']:
            print '%s: %s' % (name, getattr(self, name))
