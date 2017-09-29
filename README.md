# Load monitor

## How to add a new graph

1. Write a new munin plugin in `munin-plugins/`
2. Install the new munin plugin on xivo-load:

```
git commit
git push

ssh xivo-load
cd /usr/local/src/xivo-load-monitor/
git pull
ln -s /etc/munin/plugins/<new_plugin> /usr/local/src/xivo-load-monitor/load-monitor/munin-plugins/<new_plugin>
xivo-monitoring-update-graphics
exit
```

3. Insert new entries in the table services on load-monitor:

```
sudo -u postgres psql loadmonitorv2
INSERT INTO services VALUES (default, 'RabbitMQ memory', 'wazo_rabbitmq_memory_py-day.png', 'RabbitMQ memory', 497, 280);
INSERT INTO services_by_serveur VALUES (default, 9, 10);  # where 9 is the serveur id from table serveur and 10 is the service id created above
```

4. Update the SQL dump so that your new services can be restored
