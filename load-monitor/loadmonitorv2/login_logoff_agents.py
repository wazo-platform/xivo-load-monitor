# -*- coding: UTF-8 -*-
#!/usr/bin/python

# Copyright (C) 2013  Avencall
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

import re
import daemon
import subprocess
from time import sleep
from random import choice
from random import randint


class LogoffLoginAgent():

    def __init__(self):
        self.xivo_hostname = 'xivo-load'

    def _agent_list(self):
        cmd = [ "xivo-agentctl", "-H", self.xivo_hostname, "-c", "statuses" ]
        p = subprocess.Popen(cmd, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        agent_list = []
        for line in p.stdout:
            if re.search('Agent', line):
                agent_logged = False
                agent_number = int(re.split('/', re.split(' \(', line)[0])[1])
            else:
                if re.search('True', line):
                    agent_logged = True
                if re.search('extension', line) and agent_logged == True:
                    agent_extension = int(re.split(': ', line)[1])
                elif re.search('context', line) and agent_logged == True:
                    agent_context = re.split(': ', line)[1].strip()
                    agent_list.append({'agent_number': agent_number, 'agent_extension': agent_extension, 'agent_context': agent_context})
        return agent_list

    def _random_agent(self, agent_list):
        agent = choice(agent_list)
        return agent

    def _logoff_agent(self, agent_number):
        cmd = "xivo-agentctl -H %s -c 'logoff %s'" % (self.xivo_hostname, agent_number)
        print(cmd)
        p = subprocess.call(cmd, shell=True)

    def _logon_agent(self, agent):
        agent_number = agent['agent_number']
        agent_extension = agent['agent_extension']
        agent_context = agent['agent_context']
        cmd = "xivo-agentctl -H %s -c 'login %s %s %s'" % (self.xivo_hostname, agent_number, agent_extension, agent_context)
        print(cmd)
        subprocess.call(cmd, shell=True)

    def main(self):
        agent_list = self._agent_list()
        random_agent = self._random_agent(agent_list)
        self._logoff_agent(random_agent['agent_number'])
        sleep(randint(2,5))
        self._logon_agent(random_agent)


with daemon.DaemonContext():
    lla = LogoffLoginAgent()
    while True:
        lla.main()
        sleep(randint(2,4))
