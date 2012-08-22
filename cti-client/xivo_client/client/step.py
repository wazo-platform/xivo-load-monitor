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

import itertools
import logging
import time
from hashlib import sha1
from gevent import sleep, Timeout

logger = logging.getLogger(__name__)


class StepRunner(object):

    def __init__(self, client, steps, infos=None):
        if infos is None:
            infos = {}
        self.client = client
        self._steps = steps
        self.infos = infos
        self.command_id = itertools.count(1)

    def run(self):
        try:
            for step in self._steps:
                logger.debug('Running step %s', step)
                step.run(self)
        finally:
            self.client.close()


class ConnectStep(object):

    def run(self, runner):
        runner.client.connect()


class LoginStep(object):

    def run(self, runner):
        self._send_login_id_msg(runner)
        self._recv_login_id_response(runner)

    def _send_login_id_msg(self, runner):
        msg = self._new_login_id_msg(runner)
        runner.client.send_msg(msg)

    def _new_login_id_msg(self, runner):
        username = runner.infos['username']
        return {
            'class': 'login_id',
            'company': 'default',
            'ident': '-',
            'userlogin': username,
            'version': '9999',
            'xivoversion': '1.2',
            'commandid': runner.command_id.next(),
        }

    def _recv_login_id_response(self, runner):
        msg = runner.client.recv_msg_matching_class('login_id')
        runner.infos['session_id'] = msg['sessionid']


class PasswordStep(object):

    def run(self, runner):
        self._send_login_pass_msg(runner)
        self._recv_login_pass_response(runner)

    def _send_login_pass_msg(self, runner):
        msg = self._new_login_pass_msg(runner)
        runner.client.send_msg(msg)

    def _new_login_pass_msg(self, runner):
        password = runner.infos['password']
        session_id = runner.infos['session_id']
        hashed_password = sha1(session_id + ':' + password).hexdigest()
        return {
            'class': 'login_pass',
            'hashedpassword': hashed_password,
            'commandid': runner.command_id.next(),
        }

    def _recv_login_pass_response(self, runner):
        msg = runner.client.recv_msg_matching_class('login_pass')
        runner.infos['capalist'] = msg['capalist']


class CapasStep(object):

    def run(self, runner):
        self._send_login_capas_msg(runner)
        self._recv_login_capas_response(runner)

    def _send_login_capas_msg(self, runner):
        msg = self._new_login_capas_msg(runner)
        runner.client.send_msg(msg)

    def _new_login_capas_msg(self, runner):
        capa_id = runner.infos['capalist'][0]
        return {
            'class': 'login_capas',
            'capaid': capa_id,
            'state': 'available',
            'lastconnwins': False,
            'loginkind': 'user',
            'commandid': runner.command_id.next(),
        }

    def _recv_login_capas_response(self, runner):
        runner.client.recv_msg_matching_class('login_capas')


class LogoutStep(object):

    def run(self, runner):
        self._send_logout_msg(runner)

    def _send_logout_msg(self, runner):
        msg = {
            'class': 'logout',
            'stopper': 'disconnect',
            'commandid': runner.command_id.next(),
        }
        runner.client.send_msg(msg)


class TimerStep(object):

    def __init__(self, name):
        self._name = name

    def run(self, runner):
        runner.infos[self._name] = time.time()


class SetStep(object):

    def __init__(self, name, value):
        self._name = name
        self._value = value

    def run(self, runner):
        runner.infos[self._name] = self._value


class WaitStep(object):

    def __init__(self, wait_time_strategy):
        self._time_strategy = wait_time_strategy

    def run(self, runner):
        wait_time = self._time_strategy.get_time()
        sleep(wait_time)


class IdleStep(object):

    def __init__(self, idle_time_strategy):
        self._time_strategy = idle_time_strategy

    def run(self, runner):
        idle_time = self._time_strategy.get_time()
        with Timeout(idle_time, False):
            while True:
                runner.client.recv()


class IPBXListStep(object):

    def run(self, runner):
        self._send_getipbxlist_msg(runner)
        self._recv_getipbxlist_response(runner)

    def _send_getipbxlist_msg(self, runner):
        msg = self._new_getipbxlist_msg(runner)
        runner.client.send_msg(msg)

    def _new_getipbxlist_msg(self, runner):
        return {
            'class': 'getipbxlist',
            'commandid': runner.command_id.next(),
        }

    def _recv_getipbxlist_response(self, runner):
        msg = runner.client.recv_msg_matching_class('getipbxlist')
        runner.infos['ipbx_id'] = msg['ipbxlist'][0]


class SubscribeToQueuesStatsStep(object):

    def run(self, runner):
        self._send_subscribetoqueuesstats_msg(runner)

    def _send_subscribetoqueuesstats_msg(self, runner):
        msg = self._new_subscribetoqueuesstats_msg(runner)
        runner.client.send_msg(msg)

    def _new_subscribetoqueuesstats_msg(self, runner):
        return {
            'class': 'subscribetoqueuesstats',
            'commandid': runner.command_id.next(),
        }


class SubscribeStep(object):

    def __init__(self, message):
        self._message = message

    def run(self, runner):
        self._send_subscribe_msg(runner)

    def _send_subscribe_msg(self, runner):
        msg = self._new_subscribe_msg(runner)
        runner.client.send_msg(msg)

    def _new_subscribe_msg(self, runner):
        return {
            'class': 'subscribe',
            'message': self._message,
            'commandid': runner.command_id.next(),
        }


class InitializationStep(object):

    def run(self, runner):
        helper = _InitializationStepHelper(runner)
        helper.run()


class _InitializationStepHelper(object):

    _LIST_NAMES = ['users', 'phones', 'agents', 'queues', 'voicemails',
                   'queuemembers',
                   #'parkinglots'
                   ]

    def __init__(self, runner):
        self._infos = runner.infos
        self._recv_msg = runner.client.recv_msg
        self._send_msg = runner.client.send_msg
        self._next_command_id = runner.command_id.next
        self._item_ids = dict((name, set()) for name in self._LIST_NAMES)

    def run(self):
        self._send_getlist_listid_msgs()
        self._loop()

    def _send_getlist_listid_msgs(self):
        for list_name in self._LIST_NAMES:
            msg = {
                'class': 'getlist',
                'function': 'listid',
                'listname': list_name,
                'tipbxid': self._infos['ipbx_id'],
                'commandid': self._next_command_id(),
            }
            self._send_msg(msg)

    def _loop(self):
        while self._item_ids:
            msg = self._recv_msg()
            msg_class = msg['class']
            handler_method_name = '_handle_msg_%s' % msg_class
            handler_method = getattr(self, handler_method_name, None)
            if handler_method is not None:
                handler_method(msg)

    def _handle_msg_getlist(self, msg):
        function = msg['function']
        listname = msg['listname']
        if function == 'updateconfig':
            msg = {
                'class': 'getlist',
                'function': 'updatestatus',
                'listname': listname,
                'tid': msg['tid'],
                'tipbxid': msg['tipbxid'],
                'commandid': self._next_command_id(),
            }
            self._send_msg(msg)
            if listname == 'queues':
                msg = {
                    'class': 'getqueuesstats',
                    'on': {
                        msg['tid']: {'window': '3600', 'xqos': '60'}
                    }
                }
                self._send_msg(msg)
        elif function == 'updatestatus':
            item_id = msg['tid']
            if listname in self._item_ids:
                item_ids = self._item_ids[listname]
                item_ids.discard(item_id)
                if not item_ids:
                    del self._item_ids[listname]
        elif function == 'listid':
            item_ids = msg['list']
            if item_ids:
                self._item_ids[listname] = set(item_ids)
                for item_id in item_ids:
                    msg = {
                        'class': 'getlist',
                        'function': 'updateconfig',
                        'listname': listname,
                        'tid': item_id,
                        'tipbxid': msg['tipbxid'],
                        'commandid': self._next_command_id(),
                    }
                    self._send_msg(msg)
            else:
                del self._item_ids[listname]
