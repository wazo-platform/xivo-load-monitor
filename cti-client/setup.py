# -*- coding: UTF-8 -*-

from distutils.core import setup

setup(
    name='xivo-client-sim',
    version='1.0',
    description='A XiVO CTI client simulator.',
    url='https://gitorious.org/xivo/xivo-tools',
    packages=['xivo_client',
              'xivo_client.bin',
              'xivo_client.client',
              'xivo_client.scenario',
              'xivo_client.strategy'],
    scripts=['bin/xivo-client-sim'],
    license='GPLv3',
    long_description=open('README').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ]
)
