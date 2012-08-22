# -*- coding: UTF-8 -*-

import itertools
import unittest
from mock import Mock
from cti_client.client.step import LoginStep, PasswordStep


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
