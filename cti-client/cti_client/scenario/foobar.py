# -*- coding: UTF-8 -*-


class FoobarScenario(object):

    def __init__(self, client):
        self._client = client

    def run(self):
        try:
            self._client.connect()
            self._client.sendall('fooooobar\n')
        finally:
            self._client.close()
