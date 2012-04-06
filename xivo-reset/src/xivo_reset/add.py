# -*- coding: UTF-8 -*-

import conf
import json
from StringIO import StringIO
from xivo_reset.webservices.webservices import WebServices


def add_contexts():
    _add_internal_context()


def _add_internal_context():
    context_ws = WebServices('ipbx/system_management/context')
    content = _get_internal_context_content(context_ws)
    context_ws.add(content)


def _get_internal_context_content(context_ws):
    var_context = {
        'name': 'default',
        'displayname': 'Default',
        'entity': conf.ENTITY_NAME,
        'contexttype': 'internal',
        'contextinclude': '[]',
        'contextnumbers_user': '"user": [{"numberbeg": "%s", "numberend": "%s"}],' %
            (conf.INTERNAL_CONTEXT_USER_START, conf.INTERNAL_CONTEXT_USER_END),
        'contextnumbers_group': '',
        'contextnumbers_meetme': '',
        'contextnumbers_queue': '"queue": [{"numberbeg": "%s", "numberend": "%s"}]' %
            (conf.INTERNAL_CONTEXT_QUEUE_START, conf.INTERNAL_CONTEXT_QUEUE_END),
        'contextnumbers_incall': ''
    }
    jsonfilecontent = context_ws.get_json_file_content('context');
    jsonstr = jsonfilecontent % var_context
    content = json.loads(jsonstr)
    return content


def add_users():
    user_ws = WebServices('ipbx/pbx_settings/users')
    content = _get_users_csv_content()
    user_ws.custom({'act': 'import'}, content)


def _get_users_csv_content():
    fobj = StringIO()
    _write_users_csv(fobj)
    return fobj.getvalue()


def _write_users_csv(fobj):
    _write_header(fobj)
    for user_number in xrange(conf.NB_USERS):
        line = 'User|%04d|%s|default|sip\n' % (user_number, user_number + conf.USER_START_NUMBER)
        fobj.write(line)


def _write_header(fobj):
    fobj.write('firstname|lastname|phonenumber|context|protocol\n')


def add_agents():
    agent_ws = WebServices('callcenter/settings/agents')
    for agent_number in xrange(conf.NB_AGENTS):
        content = _get_agent_content(agent_number)
        agent_ws.add(content)


def _get_agent_content(agent_number):
    return {
        'agentfeatures': {
            'firstname': 'Agent',
            'lastname': '%04d' % agent_number,
            'number': str(agent_number + conf.AGENT_START_NUMBER),
            'passwd': '',
            'context': 'default',
            'language': '',
            'numgroup': '1',
            'musiconhold': 'default',
            'ackcall': 'no',
            'acceptdtmf': '#',
            'enddtmf': '*',
            'autologoff': '0',
            'wrapuptime': '0',
            'description': '',
        },
        'agentoptions': {
            'musiconhold': 'default',
            'ackcall': 'no',
            'autologoff': '0',
            'wrapuptime': 'default',
            'maxlogintries': '3'
        },
        'user-select': [str(agent_number + 1)]
    }


def add_queues():
    queue_ws = WebServices('callcenter/settings/queues')
    for queue_number in xrange(conf.NB_QUEUES):
        content = _get_queue_content(queue_number)
        queue_ws.add(content)


def _get_queue_content(queue_number):
    return {
        'queuefeatures': {
            'name': 'queue%d' % queue_number,
            'number': str(queue_number + conf.QUEUE_START_NUMBER),
            'context': 'default',
            'preprocess_subroutine': '',
            'timeout': '0',
            'hitting_caller': '1',
            'transfer_user': '1',
            'write_caller': '1'
        },
        'queue': {
            'strategy': 'ringall',
            'musiconhold': 'default',
            'context': 'default',
            'servicelevel': '',
            'timeout': '15',
            'retry': '5',
            'weight': '0',
            'wrapuptime': '0',
            'maxlen': '0',
            'monitor-type': '',
            'monitor-format': '',
            'joinempty': 'no',
            'leavewhenempty': 'no',
            'memberdelay': '0',
            'timeoutpriority': 'app',
            'min-announce-frequency': 60,
            'announce-position': 'yes',
            'announce-position-limit': 5
        },
        'user': [],
        'agent': [],
        'dialaction': {
            'noanswer': {
                'actiontype': 'none',
            },
            'busy': {
                'actiontype': 'none'
            },
            'congestion': {
                'actiontype': 'none'
            },
            'chanunavail': {
                'actiontype': 'none'
            }
        }
    }


def add_confrooms():
    meetme_ws = WebServices('ipbx/pbx_settings/meetme')
    for confroom_number in xrange(conf.NB_CONFROOMS):
        content = _get_confroom_content(confroom_number)
        meetme_ws.add(content)


def _get_confroom_content(confroom_number):
    confno = str(confroom_number + conf.CONFROOMS_START_NUMBER)
    return {
        'meetmefeatures': {
            'name': 'conf%s' % confroom_number,
            'confno': confno,
            'context': 'default',
            'maxusers': '0',
            'preprocess_subroutine': '',
            'description': '',
            'admin_typefrom': 'none',
            'user_mode':  'all',
            'user_announcejoinleave': 'no',
            'user_musiconhold': 'default',
            'emailfrom': 'no-reply+meetme@xivo.fr',
            'emailfromname': 'XIVO PBX',
            'emailsubject': ' XiVO  Invitation to join a conference room',
            'emailbody': 'hello\n'
        },
        'meetmeroom': {
            'pin': '0',
            'confno': confno
        }
    }
