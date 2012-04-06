# -*- coding: UTF-8 -*-

from xivo_reset import add, restore
from xivo_reset.run import run_external_command, run_internal_command,\
    run_provd_pycli_command, run_external_command_as_postgres


_SERVICES = ['spawn-fcgi', 'pf-xivo-sysconfd', 'pf-xivo-agid', 'xivo-confgend',
            'asterisk', 'xivo-ctid', 'monit']

def stop_services():
    for service in reversed(_SERVICES):
        run_external_command(['/etc/init.d/%s' % service, 'stop'])


def start_services():
    for service in _SERVICES:
        run_external_command(['/etc/init.d/%s' % service, 'start'])


def stop_provd():
    run_external_command(['/etc/init.d/pf-xivo-provd', 'stop'])


def start_provd():
    run_external_command(['/etc/init.d/pf-xivo-provd', 'start'])


def drop_asterisk_db():
    run_external_command_as_postgres('dropdb asterisk')


def recreate_asterisk_db():
    run_external_command_as_postgres('PGOPTIONS=--client-min-messages=warning psql -v dir=/usr/share/pf-xivo-base-config/datastorage -f /usr/share/pf-xivo-base-config/datastorage/asterisk.sql > /dev/null')


def insert_autocreate_prefix():
    run_external_command_as_postgres("""psql -c "INSERT INTO staticsip VALUES (DEFAULT,0,0,0,'sip.conf','general','autocreate_prefix','apvVRBYH64');\" asterisk""")


def remove_provd_devices():
    run_provd_pycli_command('devices.remove_all()')


def remove_provd_configs():
    run_provd_pycli_command('configs.remove_all()')


def recreate_base_configs():
    run_internal_command(['list-devices'])


def sip_reload():
    run_external_command(['asterisk', '-rx', 'sip reload'])


def add_contexts():
    add.add_contexts()


def add_users():
    add.add_users()


def add_confrooms():
    add.add_confrooms()

def add_agents():
    add.add_agents()


def add_queues():
    add.add_queues()


def dump_asterisk_db():
    restore.dump_db('asterisk', 'asterisk.sql')


def dump_xivo_db():
    restore.dump_db('xivo', 'xivo.sql')


def restore_asterisk_db():
    restore.restore_db('asterisk', 'asterisk.sql')


def restore_xivo_db():
    restore.restore_db('xivo', 'xivo.sql')


def store_provd_data():
    restore.store_files('/var/lib/pf-xivo-provd')


def restore_provd_data():
    restore.restore_files('/var/lib/pf-xivo-provd')
