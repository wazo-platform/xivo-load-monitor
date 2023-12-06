#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2012-2023 The Wazo Authors  (see the AUTHORS file)
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

import sys
import os
import argparse
import configparser
import time
import subprocess
import xivo_ws
import math
from lettuce.registry import world
from xivo_ws import XivoServer
from xivo_ws import User
from xivo_ws import UserLine
from xivo_ws import UserVoicemail
from xivo_ws import Agent
from xivo_ws import Queue
from xivo_ws import Group
from xivo_ws import Incall
from xivo_ws import QueueDestination
from xivo_ws import GroupDestination
from xivo_lettuce import terrain
from xivo_lettuce.manager_ws import context_manager_ws, trunksip_manager_ws
from xivo_lettuce.ssh import SSHClient

_ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))

def main():
    parsed_args = _parse_args()

    section = parsed_args.section
    if section == None:
        print('[Error] - section to use not defined')
        sys.exit(1)

    dataset = ManageDatasetWs(section)
    dataset.prepare()
    dataset.create_dataset()

def _parse_args():
    parser = _new_argument_parser()
    return parser.parse_args()

def _new_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--section', type=str,
                        help='Section to use from dataset.cfg')
    return parser

class ManageDataset(object):
    def __init__(self, section):
        config = configparser.RawConfigParser()
        config.read('dataset.cfg')

        self.ssh_user = config.get(section, 'ssh_user')

        self.host = config.get(section, 'host')
        self.user = config.get(section, 'user')
        self.secret = config.get(section, 'secret')

        self.nb_trunks = config.getint(section, 'nb_trunks')
        self.nb_default_trunks = config.getint(section, 'nb_default_trunks')
        self.trunk_context = config.get(section, 'trunk_context')
        self.nb_contexts = config.getint(section, 'nb_contexts')
 
        self.nb_users = config.getint(section, 'nb_users')
        self.users_first_line = config.getint(section, 'users_first_line')

        self.voicemail = config.getboolean(section, 'voicemail')
        self.user_ip = config.get(section,'user_ip')
 
        self.nb_agents = config.getint(section, 'nb_agents')
        self.agents_first_id = config.getint(section, 'agents_first_id')
 
        self.nb_agent_by_queue = config.getint(section, 'nb_agent_by_queue')
        self.queue_member_overlap = config.getint(section, 'queue_member_overlap')
        self.queues_first_context = config.getint(section, 'queues_first_context')
 
        self.incalls_first_line = config.getint(section, 'incalls_first_line')

        self.nb_user_in_default_context = config.getint(section, 'nb_user_in_default_context')
        self.nb_user_in_other_context = config.getint(section, 'nb_user_in_other_context')

        self.user_grp = config.get(section, 'user_grp')
        self.context_user_id = (0, 0)
        self.group_first_context = config.getint(section, 'group_first_context')
        
        self.debug = config.getboolean(section, 'debug')
        self.debug_lvl = config.getint(section, 'debug_lvl')

        self._initiate_connection()

    def create_dataset(self):
        user_list = self._user_list()
        agent_list = self._agent_list()
        queue_list = self._queue_list()

        user_start_lastname = self._user_start_lastname(user_list)
        if self.debug: print('DEBUG: user_start_lastname : %s' % user_start_lastname)
        if ( user_start_lastname + self.users_first_line ) > self.users_first_line:
            nb_user_to_create = self.nb_users - user_start_lastname
        else:
            nb_user_to_create = self.nb_users
        if self.debug: print('DEBUG: nb_user_to_create : %s' % nb_user_to_create)
        if nb_user_to_create > 0:
            self._add_users(user_start_lastname)
            self._wait_for_commit()
        if self.user_ip != 'None':
            self._update_user_ip(self.user_ip)

        if self.user_grp != 'None':
            self._fill_in_groups()

        if self.nb_agents > 0:
            agent_start_id = self._agent_start_id(agent_list)
            try:
                self._add_agents(agent_start_id, user_list)
            except IndexError:
                print('No live reload on XiVO ? Try to re-run the script :)')
                sys.exit(1)
            self._wait_for_commit()
            available_agents = self.nb_agents
        else:
            available_agents = 0

        agent_id = self._agent_id(agent_list, available_agents)
        try:
            nb_queue_add = self._nb_queue_add(available_agents, queue_list)
        except:
            nb_queue_add = 0
        queue_start_nb = self._queue_start_nb(queue_list)

        if ( nb_queue_add > ( queue_start_nb - self.queues_first_context )):
            self._add_queues(nb_queue_add, queue_start_nb, agent_id)

        nb_group_add = self._nb_group_add()
        if nb_queue_add > 0:
            # Recall of _queue_list() once queues are created
            queue_list = self._queue_list()
            queue_list_nb_id = self._queue_list_nb_id(queue_list)
            nb_incalls_add = self._nb_incalls_add(queue_list_nb_id)
            if nb_incalls_add > 0:
                self._add_incall_queue(queue_list_nb_id, nb_incalls_add)
        elif nb_group_add > 0 and self.user_grp != 'None':
            group_list = self._group_list()
            incall_list = self._incall_list()
            try:
                last_incall_number = int(incall_list[-1].number)
            except Exception as e:
                last_incall_number = 0
                if self.debug: print(e)
            if self.debug and self.debug_lvl == 2: print('########### DEBUG: last_incall_number = %s' % (last_incall_number))
            for group in group_list:
                if self.debug and self.debug_lvl == 2: print('########### DEBUG: group number = %s' % (group.number))
                group_number_condition = last_incall_number - self.incalls_first_line + self.group_first_context
                if self.debug and self.debug_lvl == 2: print('########### DEBUG: group number condition = %s' % (group_number_condition))
                if int(group.number) > group_number_condition or last_incall_number == 0:
                    self._add_incall_group(group.number, group.id)
 
    def _initiate_connection(self):
        try:
            self.xs = XivoServer(self.host, self.user, self.secret)
        except:
            print('[Error] - No connection to XiVO')
            sys.exit(1)

    def _user_last_lastname(self, user_list):
        try:
            last_id = max([int(user.lastname) for user in user_list if user.lastname != ''])
            return last_id
        except:
            print('[INFO] - No other loadtest users found, beginning with %s' % self.users_first_line)
            return 0

    def _user_list(self):
        return self.xs.users.list()

    def _user_start_lastname(self, user_list):
        user_last_lastname = self._user_last_lastname(user_list)
        if self.debug: print('DEBUG, user_last_lastname : %s' % user_last_lastname)
        if len(user_list) > 0 and user_last_lastname != 0:
            users_start_lastname = ( 1 + user_last_lastname )
        else:
            users_start_lastname = 0
        return users_start_lastname

    def _user_id_from_user_number(self, user_number):
        user_list = self._user_list()
        for user in user_list:
            try:
                if user_number == int(user.lastname) + self.users_first_line:
                    if self.debug and self.debug_lvl == 2: print('##### DEBUG: user.id : %s' % (user.id))
                    return int(user.id)
                if self.debug and self.debug_lvl == 2: print('##### DEBUG: user.lastname : %s' % (int(user.lastname)))
                if self.debug and self.debug_lvl == 2: print('##### DEBUG: user_number : %s' % (int(user_number)))
            except Exception as e:
                if self.debug: print(e)
                continue

    def _group_infos_from_group_number(self, group_number):
        group = self.xs.groups.search_by_number(group_number)
        return group[0]

    def _user_context(self, offset, user_start_lastname):
        if ( offset - user_start_lastname ) < self.nb_user_in_default_context or self.nb_user_in_other_context == 0:
            return 'default', offset + self.users_first_line
        else:
            old_context, old_position = self.context_user_id
            id_context = int(math.ceil(( offset - user_start_lastname - self.nb_user_in_default_context + 0.001) / self.nb_user_in_other_context))
            context = 'context' + str(id_context)
            if old_context != id_context:
                position = 0
            else:
                position = old_position + 1
            self.context_user_id = (id_context, position)
            line = user_start_lastname + ( id_context * 100 ) + position + self.users_first_line
            return '%s' % context, '%s' % line

    def _fill_in_groups(self):
        group_list = self._group_list()
        g_offset = 0
        u_offset = 0
        for grp_cnf in self.user_grp.split('/'):
            for number_of_groups_with_this_number_of_users in range(0, int(grp_cnf.split(',')[0])):
                u_list = []
                for number_of_users_in_this_kind_of_groups in range(0, int(grp_cnf.split(',')[1])):
                    user_number = self.users_first_line + u_offset
                    user_id = self._user_id_from_user_number(user_number)
                    if self.debug and self.debug_lvl == 2: print('### Debug: user_id is %s' % (user_id))
                    u_list.append(user_id)
                    if self.debug and self.debug_lvl == 2: print('### Debug: list is %s' % (u_list))
                    u_offset += 1
                group_number = self.group_first_context + g_offset
                group_infos = self._group_infos_from_group_number(group_number)
                self._user_to_specific_group(u_list, group_infos)
                g_offset += 1

    def _user_to_specific_group(self, l, group_infos):
        print('### Users %s to group %s' % (l, group_infos.name))
        group = Group(id=group_infos.id,
                      name=group_infos.name,
                      number=group_infos.number,
                      context=group_infos.context,
                      user_ids=l)
        self.xs.group.edit(group)

    def _agent_list(self):
        return self.xs.agents.list()

    def _agent_start_id(self, agent_list):
        if len(agent_list) > 0:
            agent_start_id = ( 1 + int(sorted([agent.number for agent in agent_list])[-1]) )
        else:
            agent_start_id = self.agents_first_id
        return agent_start_id

    def _add_users(self, user_start_lastname):
        print('Add users ..')
        users = []
        for offset in range(user_start_lastname, self.nb_users):
            user_context, line = self._user_context(offset, user_start_lastname)
            user_lastname = '%s' % (str(offset).zfill(4))
            user = User(firstname='User', lastname=user_lastname)
            user.line = UserLine(context=user_context, number=line)
            if self.voicemail:
                voicemail_name = line
                voicemail_number = line
                if self.debug: print('Activating voicemail %s' % voicemail_name)
                user.voicemail = UserVoicemail(name=voicemail_name, number=voicemail_number)
                user.language = 'fr_FR'
            users.append(user)
            if self.debug: print('DEBUG: User %s with line %s to context %s, for a total of %s users' % (user_lastname, line, user_context, self.nb_users))
        print('Adding %d users...' % len(users))
        for user in users:
            self.xs.users.import_(user)

    def _add_agents(self, agent_start_id, user_list):
        user_id = sorted([user.id for user in user_list])[-self.nb_agents:]
 
        agent_end_id = self.agents_first_id + self.nb_agents
        if agent_start_id < agent_end_id:
            print('Add agents ..')
            for offset in range(agent_start_id, agent_end_id):
                if self.debug: print('agent_start_id: %s, agent_end_id: %s, offset: %s' % (agent_start_id, agent_end_id, offset))
                agent = Agent(firstname='Agent',
                          #lastname=str( agent_start_id - agents_first_id + offset ),
                          lastname=str(offset),
                          number=offset,
                          context='default',
                          users=[ user_id[offset - agent_start_id] ])
                self.xs.agents.add(agent)
                print('Agent %s number %s added on user %s' % (agent.lastname, offset, agent.users))
 
    def _agent_id(self, agent_list, available_agents):
        return sorted([agent.id for agent in agent_list])[-available_agents:]

    def _nb_queue_add(self, available_agents, queue_list):
        return ( available_agents / ( self.nb_agent_by_queue - self.queue_member_overlap ) - len(queue_list) )

    def _queue_list(self):
        return self.xs.queues.list()

    def _group_list(self):
        return self.xs.groups.list()

    def _queue_start_nb(self, queue_list):
        if len(queue_list) > 0:
            queue_start_nb = int(queue_list[-1].number) + 1
        else:
            queue_start_nb = self.queues_first_context
        return queue_start_nb
 
    def _add_queues(self, nb_queues_add, queue_start_nb, agent_id):
        for offset in range(queue_start_nb, queue_start_nb + nb_queues_add):
            first_agent_index = ( offset - self.queues_first_context ) * ( self.nb_agent_by_queue - self.queue_member_overlap ) 
            if self.debug: print('first_agent_index: %s' % first_agent_index)
            print('Add queue..')
            queue = Queue(name='queue%s' % offset,
                          display_name='Queue %s' % offset,
                          number=offset,
                          context='default',
                          ring_strategy='rrmemory',
                          autopause=False,
                          agents=agent_id[first_agent_index:first_agent_index + self.nb_agent_by_queue])

            if len(queue.agents) > 0:
                self.xs.queues.add(queue)
            else:
                print('No agents to add to the queue, perhaps no live reload so just re-run the script')
                sys.exit(1)
            print('Queue %s number added with %s agents' % (offset, queue.agents))
 
    def _queue_list_nb_id(self, queue_list):
        return sorted((queue.number, queue.id) for queue in queue_list)

    def _incall_list(self):
        return self.xs.incalls.list()

    def _nb_incalls_add(self, queue_list_nb_id):
        return len(queue_list_nb_id) - len(self._incall_list())

    def _add_incall_queue(self, queue_list_nb_id, nb_incalls_add):
        print('Add Incalls ..')
        for queue_nb, queue_id in queue_list_nb_id[-nb_incalls_add:]:
            incall = Incall()
            incall.number = self.incalls_first_line + int(queue_nb) - self.queues_first_context
            incall.context = 'from-extern'
            incall.destination = QueueDestination(queue_id)
            print('Adding incall %s %s...' % (incall.number, incall.destination))
            self.xs.incalls.add(incall)

    def _add_incall_group(self, group_number, group_id):
        incall = Incall()
        incall.number = self.incalls_first_line + int(group_number) - self.group_first_context
        incall.context = 'from-extern'
        incall.destination = GroupDestination(group_id)
        print('Adding incall %s %s...' % (incall.number, incall.destination))
        self.xs.incalls.add(incall)

    def _nb_group_add(self):
        nb_group_add = 0
        user_grp_array = self.user_grp.split('/')
        for grp_cnf in user_grp_array:
            nb_group = int(grp_cnf.split(',')[0])
            nb_group_add += nb_group
        return nb_group_add

    def _wait_for_commit(self):
        print('Waiting for commit ...')
        i = 2
        for t in range(0, i):
            print('%s...' % (i - t))
            time.sleep(1)

class ManageDatasetWs(ManageDataset):
    def __init__(self, section):
        ManageDataset.__init__(self, section)
        hostname = self.host
        world.xivo_host = hostname
        login = self.ssh_user
        world.ssh_client_xivo = SSHClient(hostname, login)

        login = self.user
        password = self.secret
        world.ws = xivo_ws.XivoServer(hostname, login, password)

        self._init_webservices()
        self._create_pgpass_on_remote_host()

    def prepare(self):
        try:
            self._prepare_context()
            #print('DEBUG, CONTEXT SKIPPED')
        except Exception as e:
            print('Skipping, contexts already has a configuration ..')
            if self.debug: print(e)
        try:
            self._prepare_trunk()
            #print('DEBUG, TRUNK SKIPPED')
        except Exception as e:
            print('Skipping, trunks already has a configuration ..')
            if self.debug: print(e)
        if self.user_grp != 'None':
            self._add_group_to_specific_context()

    def _prepare_context(self):
        print('Configuring Context..')
        if self.nb_user_in_other_context == 0:
            default_plus_range_end = 999
        else:
            default_plus_range_end = 99
        context_manager_ws.update_contextnumbers_user('default', self.users_first_line, self.users_first_line + default_plus_range_end)
        context_manager_ws.update_contextnumbers_group('default', self.group_first_context, self.group_first_context + 99)
        context_manager_ws.update_contextnumbers_queue('default', self.queues_first_context, self.queues_first_context + 99)
        for i in range(1, self.nb_contexts + 1):
            name = 'context%s' % (i)
            user_range_start = self.users_first_line + ( 100 * i )
            user_range_end = user_range_start + 99
            group_range_start = self.group_first_context + ( 100 * i )
            group_range_end = group_range_start + 99
            queue_range_start = self.queues_first_context + ( 100 * i )
            queue_range_end = queue_range_start + 99
            context_manager_ws.add_context(name, name, 'internal')
            context_manager_ws.update_contextnumbers_user(name, user_range_start, user_range_end)
            context_manager_ws.update_contextnumbers_group(name, group_range_start, group_range_end)
            context_manager_ws.update_contextnumbers_queue(name, queue_range_start, queue_range_end)
        context_manager_ws.update_contextnumbers_incall('from-extern', 1000, 2000, 4)

    def _prepare_trunk(self):
        print('Configuring Trunk..')
        for i in range(1, self.nb_trunks + 1):
            trunk = 'trunk%s' % (i)
            # On veut n Trunks dans le contexte default
            n = self.nb_default_trunks
            if self.trunk_context != 'other':
                context = self.trunk_context
            elif i < (n + 1):
                context = 'default'
            # Les autres Trunks arrivent vers les autres contextes
            else:
                context = 'context%s' % (i - n)
            trunksip_manager_ws.add_trunksip(world.xivo_host, trunk, context, 'user')

    def _add_group_to_specific_context(self):
        flag = 0
        general_group_number = 0
        group_list = self._group_list()
        for group in self.user_grp.split('/'):
            nb_groups = int(group.split(',')[0])
            nb_user_by_grp = int(group.split(',')[1])
            context = group.split(',')[2]
            for group_number in range(0, nb_groups):
                group_line_number = general_group_number + self.group_first_context
                group_name_number = str(general_group_number).zfill(4)
                if context != 'default':
                    nb_grp_by_context = self._find_nb_grp_by_context(nb_user_by_grp)
                    if self.debug and self.debug_lvl == 2: print('DEBUG: group_number: %s, nb_grp_by_context: %s' % (group_number, nb_grp_by_context))
                    id_context = (int(math.ceil(group_number / nb_grp_by_context) +1 ))
                    context = 'context%s' % id_context
                    group_line_number = self.group_first_context + ( id_context * 100 ) + flag
                    if flag < ( nb_grp_by_context - 1 ):
                        flag += 1
                    else:
                        flag = 0
                add_group_action = True
                for group in group_list:
                    if int(group.number) == group_line_number:
                        add_group_action = False
                if add_group_action is True:
                    self._add_group(group_name_number, group_line_number, context)
                general_group_number += 1

    def _add_group(self, grp_name_nb, grp_line, context):
        print('Add group %s number %s in context %s' % (grp_name_nb, grp_line, context))
        group = Group(name='Group%s' % grp_name_nb,
                      number=grp_line,
                      context=context,
                      user_ids=[])

        self.xs.group.add(group)
        if self.debug and self.debug_lvl == 2: print('Group %s added' % (grp_name_nb))

    def _find_nb_grp_by_context(self, nb_user_by_grp):
        # Assuming that :
        # - if we are in this method, it's because we're not talking about default context
        if self.debug and self.debug_lvl == 2: print('DEBUG: nb_user_by_grp: %s' % nb_user_by_grp)
        return int(round(self.nb_user_in_other_context / nb_user_by_grp))

    def _init_webservices(self):
        ws_sql_file = os.path.join(_ROOT_DIR, 'utils', 'webservices.sql')
        cmd = ['scp', ws_sql_file, 'root@%s:/tmp/' % world.xivo_host]
        self._exec_ssh_cmd(cmd)
        cmd = ['sudo', '-u', 'postgres', 'psql', '-f', '/tmp/webservices.sql']
        world.ssh_client_xivo.check_call(cmd)

    def _create_pgpass_on_remote_host(self):
        cmd = ['echo', '*:*:asterisk:asterisk:proformatique', '>', '.pgpass']
        world.ssh_client_xivo.check_call(cmd)
        cmd = ['chmod', '600', '.pgpass']
        world.ssh_client_xivo.check_call(cmd)

    def _update_user_ip(self, ip):
        psql_cmd = 'UPDATE usersip SET HOST=\'%s\' ' % ip + 'WHERE callerid LIKE \'%User%\';'
        psql_file = os.path.join(_ROOT_DIR, 'utils', 'update_user_ip.sql')
        f = open(psql_file, 'w')
        f.write(psql_cmd)
        f.close()
        cmd = ['scp', psql_file, 'root@%s:/tmp/' % world.xivo_host]
        self._exec_ssh_cmd(cmd)
        cmd = ['sudo', '-u', 'postgres', 'psql', '-d', 'asterisk', '-f', '/tmp/update_user_ip.sql']
        print(cmd)
        world.ssh_client_xivo.check_call(cmd)

    def _exec_ssh_cmd(self, cmd):
        p = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)

        (stdoutdata, stderrdata) = p.communicate()

        if p.returncode != 0:
            print(stdoutdata)
            print(stderrdata)

        return stdoutdata

if __name__ == "__main__":
    main()
