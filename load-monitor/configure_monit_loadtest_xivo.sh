#!/bin/bash
apt-get update
apt-get -y install git lsof python3-pip build-essential python3-dev libdbd-pg-perl libnet-dns-perl
mkdir -p /usr/local/src/git
cd /usr/local/src/
git clone https://github.com/wazo-platform/xivo-load-monitor.git
pip install psutil PyMunin3
cd /etc/munin/plugins/
ln -s /usr/local/src/xivo-load-monitor/load-monitor/munin-plugins/asterisk_calls_processed.py .
ln -s /usr/local/src/xivo-load-monitor/load-monitor/munin-plugins/asterisk_simultaneous_calls_average.py .
ln -s /usr/local/src/xivo-load-monitor/load-monitor/munin-plugins/pgsql_mem.py .
ln -s /usr/local/src/xivo-load-monitor/load-monitor/munin-plugins/xivo_asterisk_file_descriptors .
ln -s /usr/local/src/xivo-load-monitor/load-monitor/munin-plugins/xivo_asterisk_freeze_detect.py .
ln -s /usr/local/src/xivo-load-monitor/load-monitor/munin-plugins/xivo_asterisk_mem.py .
ln -s /usr/local/src/xivo-load-monitor/load-monitor/munin-plugins/xivo_asterisk_socket.py .
#ln -s /usr/local/src/xivo-load-monitor/load-monitor/munin-plugins/xivo_disk_space_by_call_munin.py .
ln -s /usr/share/munin/plugins/postgres_connections_db .
sed -i 's/127\.0\.0\.1/0\.0\.0\.0/' /etc/munin/munin-node.conf.tmpl
sed -i 's/\^127\\\.0\\\.0\\\.1\$$/\^\.\*\$/' /etc/munin/munin-node.conf.tmpl
wazo-monitoring-update-graphics
systemctl restart munin-node
echo 'Munin configuration finished'
