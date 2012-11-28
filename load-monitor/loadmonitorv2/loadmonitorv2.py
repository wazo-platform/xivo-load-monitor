from flask import Flask, redirect, url_for, render_template, request, flash
from flask.ext.wtf import Form, TextField, SelectField, SelectMultipleField, Required, validators
import psycopg2
import sys
import re

app = Flask(__name__)

class Loadmonitorv2Functions:
    def __init__(self):
        pg_host = '10.38.1.252'
        pg_username = 'loadmonitorv2'
        pg_password = 'loadmonitorv2'
        pg_db = 'loadmonitorv2'
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
                srv_id = self._id_from_name(srv['name'])[0]
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

    def _id_from_name(self, name):
        sql = 'SELECT serveur.id FROM serveur WHERE serveur.nom = \'%s\'' % (name)
        return self._execute_and_fetch_sql(sql)

    def _complete_uri(self, uri, server_params):
        munin_ip = self._munin_ip(server_params[0])[0][0]
        name = server_params[1]
        domain = server_params[3]
        complete_uri = 'http://' + munin_ip + '/munin/' + domain + '/' + name + '.' + domain + '/' + uri
        print complete_uri
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
    lmv2 = Loadmonitorv2Functions()
    types_choices = lmv2._strize(lmv2.server_types_choices())
    munin_choices = lmv2._strize(lmv2.munin_servers())
    services_choices = lmv2._strize(lmv2.service_list())
    print(munin_choices)
    print(types_choices)

    name = TextField('nom', [validators.Required()])
    ip = TextField('ip', [validators.Required()])
    domain = TextField('domaine', [validators.Required()])
    name = TextField('nom')
    ip = TextField('ip')
    domain = TextField('domaine')
    server_type = SelectField(u'Type du serveur', choices=types_choices)
    watcher = SelectField(u'Serveur Munin associe', choices=munin_choices)
    services = SelectMultipleField(u'Services monitores', choices=services_choices)

@app.route('/')
def hello():
    lmv2 = Loadmonitorv2Functions()
    xivo_list = lmv2.xivo_list()
    lmv2.close_conn()
    server = xivo_list[0][1]
    return redirect(url_for('show_server', server=server))

@app.route('/ServerSelect/<server>')
def show_server(server):
    # get list of graphs for 'server'
    lmv2 = Loadmonitorv2Functions()
    server_params = lmv2.server_params(server)[0]
    graph_list = lmv2.gen_page(server_params)
    xivo_server_list = lmv2.xivo_server_list()
    return render_template('graphs.html', graphs=graph_list, server=server, server_list=xivo_server_list)

@app.route('/AddServer/', methods=('GET', 'POST'))
def add_server():
    form = AddServerForm()
    if form.validate_on_submit():
        flash('Success')
        new_server = {'name':form.name.data,
                    'ip':form.ip.data,
                    'domain':form.domain.data,
                    'server_type':form.server_type.data,
                    'watcher':form.watcher.data,
                    'services':form.services.data}
        print('########################################')
        print(new_server)
        print('########################################')
        lmv2 = Loadmonitorv2Functions()
        lmv2.add_server(new_server)
        return redirect(url_for('hello'))
    else:
        print('DEBUG ===> %s' % (form.validate_on_submit()))

    return render_template('add-server.html', form=form)

if __name__ == "__main__":
    app.debug = True
    app.secret_key = '\xbd5\xcc\xa3\xfd\x7f\x15WY\xc9J[\x07\n\x1d\xa7\xc4\x14k\xecL%7.'
    app.run(host='0.0.0.0')

