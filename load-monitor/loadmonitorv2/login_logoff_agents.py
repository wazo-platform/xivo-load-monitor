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
import sys
import daemon
import subprocess
import argparse
from time import sleep
from random import choice
from random import randint

def main():
    parsed_args = _parse_args()

    hostname = parsed_args.hostname
    if hostname == None:
        print '[Error] - hostname not defined'
        sys.exit(1)

    with daemon.DaemonContext():
        lla = LogoffLoginAgent(hostname)
        unlog_agents = []
        try:
            while True:
                unlog_agents = lla.main(unlog_agents)
                sleep(randint(2,4))
        except:
            sys.exit(1)

def _parse_args():
    parser = _new_argument_parser()
    return parser.parse_args()

def _new_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--hostname', type=str,
                        help='Hostname of the tested server')
    return parser


class LogoffLoginAgent(object):

    def __init__(self, hostname):
        self.xivo_hostname = hostname

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

    def _count_and_logoff(self, unlog_agents):
        agent_list = self._agent_list()
        random_agent = self._random_agent(agent_list)
        self._logoff_agent(random_agent['agent_number'])
        unlog_agents.append(random_agent)
        return unlog_agents

    def _count_and_logon(self, unlog_agents):
        key = randint(0,len(unlog_agents)) - 1
        self._logon_agent(unlog_agents[key])
        del unlog_agents[key]
        return unlog_agents

    def main(self, unlog_agents):
        wtd = randint(0,1)
        if len(unlog_agents) < 5:
            unlog_agents = self._count_and_logoff(unlog_agents)
        elif wtd == 0 and len(unlog_agents) < 51:
            unlog_agents = self._count_and_logoff(unlog_agents)
        else:
            unlog_agents = self._count_and_logon(unlog_agents)
        return unlog_agents


if __name__ == "__main__":
    main()
