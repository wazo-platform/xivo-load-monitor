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

import unittest
from mock import Mock
from xivo_client.client.cti import CTIClient
from xivo_client.exception import AlreadyConnectedError


class TestCTIClient(unittest.TestCase):

    def test_connect_call_new_socket(self):
        cti_client = self._new_cti_client()
        cti_client._new_socket = Mock()

        cti_client.connect()

        cti_client._new_socket.assert_called_once_with()

    def _new_cti_client(self):
        return CTIClient('example.org', 5003)

    def _new_cti_client_with_mocked_socket(self):
        client = self._new_cti_client()
        client._sock = Mock()
        return client

    def test_connect_raise_error_if_already_connected(self):
        cti_client = self._new_cti_client()
        cti_client._new_socket = Mock()

        cti_client.connect()
        self.assertRaises(AlreadyConnectedError, cti_client.connect)

    def test_close_doesnt_raise_error(self):
        cti_client = self._new_cti_client()
        cti_client.close()

    def test_close_close_underlyind_socket_once(self):
        sock = Mock()
        cti_client = self._new_cti_client()
        cti_client._sock = sock

        cti_client.close()
        cti_client.close()

        sock.close.assert_called_once_with()

    def test_recv_call_underlying_socket(self):
        cti_client = self._new_cti_client_with_mocked_socket()
        cti_client._sock.recv.return_value = 'foobar'

        data = cti_client.recv()

        cti_client._sock.recv.assert_called_once_with(cti_client.DEFAULT_BUFSIZE)
        self.assertEqual('foobar', data)

    def test_recv_msg(self):
        cti_client = self._new_cti_client_with_mocked_socket()
        cti_client._sock.recv.return_value = '{"a": 1}\n{"b": 2}\n'

        msg = cti_client.recv_msg()

        cti_client._sock.recv.assert_called_once_with(cti_client.DEFAULT_BUFSIZE)
        self.assertEqual({'a': 1}, msg)

    def test_recv_msg_wait_on_incomplete_msg(self):
        cti_client = self._new_cti_client_with_mocked_socket()
        cti_client._sock.recv.side_effect = ['{"a":', ' 1}\n{"b":', ' 2}\n']

        msg1 = cti_client.recv_msg()
        msg2 = cti_client.recv_msg()

        self.assertEqual({'a': 1}, msg1)
        self.assertEqual({'b': 2}, msg2)

    def test_send_call_underlying_socket(self):
        cti_client = self._new_cti_client_with_mocked_socket()
        cti_client._sock.send.return_value = 123

        n = cti_client.send('foobar')

        cti_client._sock.send.assert_called_once_with('foobar')
        self.assertEqual(123, n)

    def test_sendall_call_underlying_socket(self):
        cti_client = self._new_cti_client_with_mocked_socket()

        cti_client.sendall('foobar')

        cti_client._sock.sendall.assert_called_once_with('foobar')

    def test_send_msg_call_underlying_socket(self):
        cti_client = self._new_cti_client_with_mocked_socket()

        cti_client.send_msg({'a': 'b'})

        cti_client._sock.sendall.assert_called_once_with('{"a": "b"}\n')
