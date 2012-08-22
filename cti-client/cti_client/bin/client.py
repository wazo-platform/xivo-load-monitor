# -*- coding: UTF-8 -*-

import argparse
import logging
import cti_client.client.step
import cti_client.scenario.foobar
import cti_client.scenario.null
import cti_client.scenario.standard
import cti_client.strategy.prespawn
import cti_client.strategy.spawn
import cti_client.strategy.time
from cti_client.client.cti import CTIClient
from cti_client.runner import ScenarioRunner
from cti_client.scenario.standard import StandardScenarioStatistics


def main():
    _init_logging()
    parsed_args = _parse_args()

    _set_logging_level(parsed_args.verbose)

    stats = StandardScenarioStatistics()
    parsed_args.stats = stats

    config = _load_config_file(parsed_args.conf, parsed_args)

    scenario_runner = ScenarioRunner(config['scenarios'],
                                     config['spawn_strategy'],
                                     config['pre_spawn_strategy'])
    try:
        scenario_runner.run()
    finally:
        stats.print_stats()


def _set_logging_level(verbosity):
    log_level = logging.WARNING
    if verbosity == 1:
        log_level = logging.INFO
    elif verbosity > 1:
        log_level = logging.DEBUG
    logger = logging.getLogger()
    logger.setLevel(log_level)


def _load_config_file(filename, config_args):
    config_globals = {}
    config_globals.update(cti_client.scenario.foobar.__dict__)
    config_globals.update(cti_client.scenario.null.__dict__)
    config_globals.update(cti_client.scenario.standard.__dict__)
    config_globals.update(cti_client.client.step.__dict__)
    config_globals.update(cti_client.strategy.prespawn.__dict__)
    config_globals.update(cti_client.strategy.spawn.__dict__)
    config_globals.update(cti_client.strategy.time.__dict__)
    config_globals['CTIClient'] = CTIClient
    config_globals['args'] = config_args
    execfile(filename, config_globals)
    return config_globals


def _init_logging():
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--conf', default='etc/conf.py',
                        help='configuration file')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='increase verbosity')
    parser.add_argument('-p', '--port', type=int, default=CTIClient.DEFAULT_PORT,
                        help='CTI port')
    parser.add_argument('hostname',
                        help='CTI server hostname')
    return parser.parse_args()


if __name__ == '__main__':
    main()
