# Load monitor

## How to add a new graph

1. Write a new munin plugin in `munin-plugins/`
2. Install the new munin plugin on xivo-load:

```
git commit
git push

ssh load-monitor 
cd /usr/local/xivo-load-monitor/
git pull
ln -s /etc/munin/plugins/<new_plugin> /usr/local/xivo-load-monitor/loadmonitorv2/munin-plugins/<new_plugin>
xivo-monitoring-update-graphics
exit
```

3. Insert new entries in the table services on load-monitor:

```
sudo -u postgres psql loadmonitorv2
insert into services values (default, 'RabbitMQ memory', 'wazo_rabbitmq_memory_py-day.png', 'RabbitMQ memory', 497, 280);
insert into services_by_serveur values (default, 9, 10);  # where 9 is the serveur id from table serveur and 10 is the service id created above
```

4. Update the SQL dump so that your new services can be restored
