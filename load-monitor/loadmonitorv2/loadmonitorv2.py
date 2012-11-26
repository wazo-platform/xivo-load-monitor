from flask import Flask, redirect, url_for, render_template
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
        return self._execute_sql(sql)

    def server_params(self, server_name):
        sql = 'SELECT * FROM serveur WHERE nom = \'%s\'' % (server_name)
        return self._execute_sql(sql)

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
        return self._execute_sql(sql)

    def _munin_ip(self, server_id):
        sql = 'SELECT serveur.ip FROM serveur WHERE serveur.id IN ( SELECT watched.id_watched_by FROM watched WHERE id_watched = %s )' % (server_id)
        return self._execute_sql(sql)

    def _list_services_by_server(self, server_id):
        sql = 'SELECT * from services_by_serveur WHERE id_serveur = %s' % (server_id)
        return self._execute_sql(sql)

    def _execute_sql(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()

@app.route('/')
def hello():
    lmv2 = Loadmonitorv2Functions()
    xivo_list = lmv2.xivo_list()
    lmv2.close_conn()
    server = xivo_list[0][1]
    return redirect('http://127.0.0.1:5000/ServerSelect/%s' % server)

@app.route('/ServerSelect/<server>')
def show_server(server):
    # get list of graphs for 'server'
    lmv2 = Loadmonitorv2Functions()
    server_params = lmv2.server_params(server)[0]
    graph_liste = lmv2.gen_page(server_params)
    print(graph_liste)
    return render_template('graphs.html', graphs=graph_liste, server=server)

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
