from lib.mytime import TimeConvertor
import re
import sys

convertor=TimeConvertor()

# 1315465054
time_patten = re.compile("[0-9]{10}")

for line in sys.stdin.readlines():
    m = re.search(time_patten,line)
    print convertor.to_readable(m.group(0))

