#!/bin/bash
apt-get update
apt-get -y install git lsof python-pip build-essential python-dev
mkdir -p /usr/local/src/git
cd /usr/local/src/git/
git clone git://gitorious.org/xivo/xivo-tools.git
git clone git://github.com/samuel/python-munin.git
cd python-munin/
python setup.py build
python setup.py install
pip install psutil
cd /etc/munin/plugins/
ln -s /usr/local/src/git/xivo-tools/load-monitor/munin-plugins/asterisk_calls_processed.py .
ln -s /usr/local/src/git/xivo-tools/load-monitor/munin-plugins/pgsql_mem.py
ln -s /usr/local/src/git/xivo-tools/load-monitor/munin-plugins/xivo_asterisk_file_descriptors
ln -s /usr/local/src/git/xivo-tools/load-monitor/munin-plugins/xivo_asterisk_freeze_detect.py
ln -s /usr/local/src/git/xivo-tools/load-monitor/munin-plugins/xivo_asterisk_mem.py
ln -s /usr/local/src/git/xivo-tools/load-monitor/munin-plugins/xivo_asterisk_socket.py
ln -s /usr/local/src/git/xivo-tools/load-monitor/munin-plugins/xivo_ctid_mem.py
ln -s /usr/local/src/git/xivo-tools/load-monitor/munin-plugins/xivo_ctid_socket.py
#ln -s /usr/local/src/git/xivo-tools/load-monitor/munin-plugins/xivo_disk_space_by_call_munin.py
sed -i 's/127\.0\.0\.1/0\.0\.0\.0/' /etc/munin/munin-node.conf.tmpl
sed -i 's/\^127\\\.0\\\.0\\\.1\$$/\^\.\*\$/' /etc/munin/munin-node.conf.tmpl
xivo-monitoring-update-graphics
/etc/init.d/munin-node restart
echo 'Munin configuration finished'
