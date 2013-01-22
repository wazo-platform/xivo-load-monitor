# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

import csv, os, glob, time, string

def list_sip_tests():
    folder = '/var/www/load-monitor/logs/sip_logs/'
    date_file_list = []
    for logfile in glob.glob(folder + '/*.csv'):
        # retrieves the stats for the current file as a tuple
        # (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime)
        # the tuple element mtime at index 8 is the last-modified-date
        stats = os.stat(logfile)
        # create tuple (year yyyy, month(1-12), day(1-31), hour(0-23), minute(0-59), second(0-59),
        # weekday(0-6, 0 is monday), Julian day(1-366), daylight flag(-1,0 or 1)) from seconds since epoch
        # note:  this tuple can be sorted properly by date and time
        lastmod_date = time.localtime(stats[8])
        # create list of tuples ready for sorting by date
        date_file_tuple = lastmod_date, logfile
        date_file_list.append(date_file_tuple)
    date_file_list.sort()
    date_file_list.reverse()  # newest mod date now first
    file_name_list = []
    for file_info in date_file_list:
        # extract just the filename
        folder_path, file_name = os.path.split(file_info[1])
        file_name_list.append(file_name)
    return file_name_list

def get_tests_status(log_file_name):
    scenario, pid, ext = string.split(log_file_name, '_')
    if os.path.exists('/proc/%s' % pid):
        process_state = 'RUNNING'
    else:
        process_state = 'NOT RUNNING'
    return process_state

def read_log_file( scenario_file ):
	handler = csv.reader(open(scenario_file), delimiter=';', quotechar='"')
	csvrows = []
	for row in handler:
		csvrows.append(row)
	return csvrows

#readed = read_log_file("/home/hsbzh/Work/Apache/load-tester-results/csv/scenario_18402_.csv")

def print_results_title( results, scenario_name ):
	starting_time = results[1][2]
	print starting_time

#print_results_title(readed, scenario_name)
