#!/usr/bin/python

#./100005135_152612300.11360.flv.log:--2011-03-25 00:12:17--  http://503.gt3.vkadre.ru/assets/videos/f4e9fbec00b0-94492708.vk.flv
#./100005135_152612300.11360.flv.log:2011-03-25 00:12:20 (145 KB/s) - `./var/tmp/resource/media/2011-03-25/vkontakte/00/100005135_152612300.11360.flv' saved [345319/345319]

#./100218288_157507600.21251.mp4.log:--2011-03-25 04:30:59--  http://cs12871.vkontakte.ru/u85281364/video/992114eabd.240.mp4
#./100218288_157507600.21251.mp4.log:2011-03-25 04:30:59 ERROR 404: Not Found.

import sys
import re
from datetime import datetime
import time

start_patten = re.compile("http:")
success_patten = re.compile("saved")
error_patten = re.compile("ERROR")
date_patten = re.compile("(2011-03-25 [0-9,:]*)")
t = []

for line in sys.stdin.readlines():
    if start_patten.search(line):
        m = re.search(date_patten,line)
        t1=datetime.strptime(m.group(0), "%Y-%m-%d %H:%M:%S")
    if success_patten.search(line):
        m = re.search(date_patten,line)
        t2=datetime.strptime(m.group(0), "%Y-%m-%d %H:%M:%S")
        t.append( time.mktime(t2.timetuple())-time.mktime(t1.timetuple()) )

print max(t)
print sum(t, 0.0) / len(t)


#    if error_patten.search(line):
#        print "ERROR"

