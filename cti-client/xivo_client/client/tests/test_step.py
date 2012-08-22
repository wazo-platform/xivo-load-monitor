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
import unittest
from mock import Mock
from xivo_client.client.step import LoginStep, PasswordStep


def _new_runner(infos):
    runner = Mock()
    runner.infos = infos
    runner.command_id = itertools.repeat(1)
    return runner


class TestLoginStep(unittest.TestCase):

    def test_send_login_id_msg(self):
        runner = _new_runner({'username': 'user'})
        step = LoginStep()

        step._send_login_id_msg(runner)

        expected_sent_msg = {
            'class': 'login_id',
            'commandid': 1,
            'company': 'default',
            'ident': '-',
            'userlogin': 'user',
            'version': '9999',
            'xivoversion': '1.2',
        }
        runner.client.send_msg.assert_called_once_with(expected_sent_msg)


class TestPasswordStep(unittest.TestCase):

    def test_send_login_pass_msg(self):
        runner = _new_runner({'session_id': 'A2tbvyFkW4', 'password': 'pass'})
        step = PasswordStep()

        step._send_login_pass_msg(runner)

        expected_sent_msg = {
            'class': 'login_pass',
            'commandid': 1,
            'hashedpassword': '9b324fa73f623d0f8dfc8939b1fc9a2c0720004e',
        }
        runner.client.send_msg.assert_called_once_with(expected_sent_msg)
