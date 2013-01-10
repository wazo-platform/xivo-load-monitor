# -*- coding: UTF-8 -*-

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

import calendar
import conf
import re
from flask import Flask, redirect, url_for, render_template, get_template_attribute, request, flash
from loadmonitorv2 import Loadmonitorv2, AddServerForm, LaunchLoadtest


app = Flask(__name__)

@app.route('/')
def hello():
    lmv2 = Loadmonitorv2(conf)
    xivo_list = lmv2.xivo_list()
    lmv2.close_conn()
    if xivo_list:
        server = xivo_list[0][1]
    else:
        server = 'None'
    return redirect(url_for('show_server', server=server))

@app.route('/ServerSelect/<server>')
def show_server(server):
    # get list of graphs for 'server'
    if server != 'None':
        lmv2 = Loadmonitorv2(conf)
        server_params = lmv2.server_params(server)[0]
        graph_list = lmv2.gen_page(server_params)
        xivo_server_list = lmv2.xivo_server_list()
        server_list = {}
        start_test_date_format = 'No test running'
        for servername in xivo_server_list:
            pid = lmv2.is_test_running(servername[0])
            if pid is not None:
                server_list.update({servername[0]: 'true'})
                if servername[0] == server:
                    start_test_date = lmv2.start_test_date(servername[0])
                    start_test_date_format = '%s %s - %s:%s' % (start_test_date.day, calendar.month_name[start_test_date.month], start_test_date.hour, start_test_date.minute)
            else:
                server_list.update({servername[0]: 'false'})
    else:
        graph_list=[]
        xivo_server_list=[]
    leftmenu_macro = get_template_attribute('_leftmenu.html', 'left_menu')
    return render_template('graphs.html', leftmenu_macro=leftmenu_macro(server_list, server), graphs=graph_list, server=server, start_test_date=start_test_date_format)

@app.route('/AddServer/', methods=('GET', 'POST'))
def add_server():
    form = AddServerForm(csrf_enabled=False)
    if form.validate_on_submit():
        new_server = {'name':form.name.data,
                    'ip':form.ip.data,
                    'domain':form.domain.data,
                    'server_type':form.server_type.data,
                    'watcher':form.watcher.data,
                    'services':form.services.data}
        lmv2 = Loadmonitorv2(conf)
        lmv2.add_server(new_server)
        return redirect(url_for('hello'))
    else:
        print('DEBUG ===> %s' % (form.validate_on_submit()))

    return render_template('add-server.html', form=form)

@app.route('/LaunchTest/', methods=('GET', 'POST'))
def launch_test():
    form = LaunchLoadtest(csrf_enabled=False)
    if form.validate_on_submit():
        """
        loadtest_params = {'server':form.server.data,
                           'rate':form.rate.data,
                           'rate_period':str(int(form.rate_period.data) * 1000)}
        """
        loadtest_params = {'server':form.server.data}
        lmv2 = Loadmonitorv2(conf)
        lmv2.launch_loadtest(loadtest_params)
        return redirect(url_for('hello'))
    return render_template('launch-test.html', form=form)

@app.route('/StopTest/<servername>')
def stop_test(servername):
    lmv2 = Loadmonitorv2(conf)
    lmv2.stop_loadtest(servername)
    return redirect(url_for('hello'))

if __name__ == "__main__":
    app.debug = True
    app.secret_key = '\xbd5\xcc\xa3\xfd\x7f\x15WY\xc9J[\x07\n\x1d\xa7\xc4\x14k\xecL%7.'
    app.run(host='0.0.0.0')

