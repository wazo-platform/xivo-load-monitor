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

import psycopg2
import re
import sys
import conf
import subprocess
import os
import psutil
from flask.ext.wtf import Form, TextField, SelectField, SelectMultipleField, Required, validators


class Loadmonitorv2(object):

    def __init__(self, conf):
        self.sipp = conf.sipp
        self.xivo_loadtest = conf.xivo_loadtest
        self.general_log_dir = conf.general_log_dir
        pg_host = conf.pg_host
        pg_username = conf.pg_username
        pg_password = conf.pg_password
        pg_db = conf.pg_db
        conn_string = 'host=%s dbname=%s user=%s password=%s' % (pg_host, pg_db, pg_username, pg_password)
        self.conn = psycopg2.connect(conn_string)

        try:
            self.cursor = self.conn.cursor()
        except:
            print('Database initialization error')
            sys.exit(1)

    def close_conn(self):
        self.conn.close()

    def xivo_list(self):
        sql = 'SELECT * FROM serveur WHERE type=1'
        return self._execute_and_fetch_sql(sql)

    def server_params(self, server_name):
        sql = 'SELECT * FROM serveur WHERE nom = \'%s\'' % (server_name)
        return self._execute_and_fetch_sql(sql)

    def gen_page(self, server_params):
        services_by_server = self._list_services(server_params)
        liste = []
        for service_by_server in services_by_server:
            service_id = service_by_server[2]
            service = self._service(service_id)[0]

            title = service[1]
            uri = service[2]
            alt = service[3]
            width = service[4]
            height = service[5]

            complete_uri = self._complete_uri(uri, server_params)
            day_uri = '%s alt=%s width=%s height=%s' % (complete_uri, alt, width, height)
            week_uri = re.sub('day', 'week', day_uri)
            liste.append({'title': title, 'day_uri': day_uri, 'week_uri': week_uri})
        
        return liste

    def xivo_server_list(self):
        sql = 'SELECT serveur.nom FROM serveur WHERE serveur.type = \'1\''
        return self._execute_and_fetch_sql(sql)

    def server_types_choices(self):
        sql = 'SELECT * FROM serveur_type'
        return self._execute_and_fetch_sql(sql)

    def munin_servers(self):
        sql = 'SELECT serveur.id, serveur.nom FROM serveur WHERE type = \'2\' OR type = \'5\''
        return self._execute_and_fetch_sql(sql)

    def service_list(self):
        sql = 'SELECT services.id, services.service FROM services ORDER BY id'
        return self._execute_and_fetch_sql(sql)

    def add_server(self, srv):
        try:
            sql = 'INSERT INTO serveur (nom, ip, domain, type) VALUES (\'%s\', \'%s\', \'%s\', \'%i\')' % (srv['name'], srv['ip'], srv['domain'], int(srv['server_type']))
            print(sql)
            self._execute_sql(sql)
        except Exception as e:
            print(e)
            return False
        try:
            sql_commit = 'commit'
            print(sql_commit)
            self._execute_sql(sql_commit)
            if int(srv['server_type']) == 1:
                srv_id = self._id_from_name(srv['name'])
                sql_watcher = 'INSERT INTO watched (id_watched, id_watched_by) VALUES (%s, %s)' % (srv_id, srv['watcher'])
                print(sql_watcher)
                self._execute_sql(sql_watcher)
                for service in srv['services']:
                    sql_service = 'INSERT INTO services_by_serveur (id_serveur, id_service) VALUES (%s, %s)' % (srv_id, service)
                    print sql_service
                    self._execute_sql(sql_service)
        except Exception as e:
            print(e)
            return False
        return True

    def launch_loadtest(self, loadtest_params):
        src_ip = self._server_munin_ip(loadtest_params['server'])
        dest_ip = self._server_ip(loadtest_params['server'])
        if not self.is_test_running(self._name_from_id(loadtest_params['server'])):
            cmd = '{loadtest_path}/load-tester -c {loadtest_path}/etc/conf-{servername}.py -d {lmv2_path}/logs/sip_logs/{servername}/ {loadtest_path}/scenarios/call-then-hangup/'.format(loadtest_path = self.xivo_loadtest, servername = self._name_from_id(loadtest_params['server']), lmv2_path = '/var/www/load-monitor-v2')
            print('################ COMMAND:')
            print(cmd)
            try:
                p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                output = p.communicate()[0]
            except Exception, e:
                output = str(e.output)
        pid = re.split('\]', re.split('\[', output)[1])[0]
        self._store_pid(pid, loadtest_params['server'])

    def stop_loadtest(self, servername):
        pid = self._pid_of_running_test(servername)
        cmd = 'sudo kill %s' % (pid)
        subprocess.call(cmd, shell=True)

    def is_test_running(self, servername):
        pid = self._pid_of_running_test(servername)
        if pid:
            for pid_item in psutil.get_pid_list():
                if pid_item == pid:
                    return pid

    def server_choices(self):
        sql = 'SELECT serveur.id, serveur.nom FROM serveur WHERE type = \'1\''
        return self._execute_and_fetch_sql(sql)

    def _id_from_name(self, name):
        sql = 'SELECT serveur.id FROM serveur WHERE serveur.nom = \'%s\'' % (name)
        return self._execute_and_fetch_sql(sql)[0][0]

    def _name_from_id(self, srv_id):
        sql = 'SELECT serveur.nom FROM serveur WHERE serveur.id = %s' % (srv_id)
        return self._execute_and_fetch_sql(sql)[0][0]

    def _complete_uri(self, uri, server_params):
        munin_ip = self._munin_ip(server_params[0])[0][0]
        name = server_params[1]
        domain = server_params[3]
        complete_uri = 'http://' + munin_ip + '/munin/' + domain + '/' + name + '.' + domain + '/' + uri
        return complete_uri

    def _list_services(self, server_params):
        server_id = server_params[0]
        server = server_params[1]
        domain = server_params[3]

        munin_ip = self._munin_ip(server_id)[0][0]
        services = self._list_services_by_server(server_id)
        return services

    def _service(self, id_service):
        sql = 'SELECT * FROM services WHERE id = %s' % (id_service)
        return self._execute_and_fetch_sql(sql)

    def _munin_ip(self, server_id):
        sql = 'SELECT serveur.ip FROM serveur WHERE serveur.id IN ( SELECT watched.id_watched_by FROM watched WHERE id_watched = %s )' % (server_id)
        return self._execute_and_fetch_sql(sql)

    def _list_services_by_server(self, server_id):
        sql = 'SELECT * from services_by_serveur WHERE id_serveur = %s' % (server_id)
        return self._execute_and_fetch_sql(sql)

    def _server_ip(self, server):
        sql = 'SELECT ip FROM serveur WHERE id = %s' % (server)
        return self._execute_and_fetch_sql(sql)[0][0]

    def _server_munin_ip(self, server):
        sql = 'SELECT serveur.ip FROM serveur WHERE serveur.id IN ( SELECT watched.id_watched_by FROM watched WHERE watched.id_watched = %s )' % (server)
        return self._execute_and_fetch_sql(sql)[0][0]

    def _store_pid(self, pid, server_id):
        sql = 'INSERT INTO log_info (id_server, pid_test, start_time) VALUES (%s, %s, now())' % (server_id, pid)
        self._execute_sql(sql)

    def _pid_of_running_test(self, servername):
        server_id = self._id_from_name(servername)
        sql = 'SELECT pid_test FROM log_info WHERE id_server = %s ORDER BY start_time DESC' % (server_id)
        return self._execute_and_fetch_sql(sql)

    def _execute_and_fetch_sql(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def _execute_sql(self, sql):
        try:
            self.cursor.execute(sql)
            return True
        except:
            return False

    def _strize(self, data):
        return [ (str(x[0]), x[1]) for x in data]

class AddServerForm(Form):
    lmv2 = Loadmonitorv2(conf)
    types_choices = lmv2._strize(lmv2.server_types_choices())
    munin_choices = lmv2._strize(lmv2.munin_servers())
    services_choices = lmv2._strize(lmv2.service_list())

    name = TextField('nom', [validators.Required()])
    ip = TextField('ip', [validators.Required()])
    domain = TextField('domaine', [validators.Required()])
    name = TextField('nom')
    ip = TextField('ip')
    domain = TextField('domaine')
    server_type = SelectField(u'Type du serveur', choices=types_choices)
    watcher = SelectField(u'Serveur Munin associe', choices=munin_choices)
    services = SelectMultipleField(u'Services monitores', choices=services_choices)

class LaunchLoadtest(Form):
    lmv2 = Loadmonitorv2(conf)
    server_choices = lmv2._strize(lmv2.server_choices())

    server = SelectField(u'Serveur cible', choices=server_choices)
    rate = TextField(u'Nombre d\'appels / periode (format: 1.0 || 2.0 || ...)', [validators.Required()])
    rate_period = TextField(u'Periode entre 2*n appels (en s)', [validators.Required()])

