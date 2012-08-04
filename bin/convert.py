#!/usr/bin/python

from time import gmtime, strftime
import getopt, sys

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)

def main():
    no_date = False
    more_detail = False
    d={}
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ndf:", ["help", "output="])
    except getopt.GetoptError, err:
        raise Usage(err)
        sys.exit(2)

    for o, a in opts:
        if o == "-n":
            no_date = True
        elif o == "-f":
            target_file = a
        elif o == "-d":
            more_detail = True
        else:
            assert False, "unhandled option"
    try:
        target_file
    except NameError, err:
        #raise Usage(err)
        print """Usage: ./convert.py [-n] [-d] -f target_file
  -n  don't print date or hour information
  -d  statics in hourly, not in daily
  -f  the file to process"""
        #raise Usage("Usage: ./convert.py [-n] [-d] -f target_file")
        sys.exit(3)

    with open(target_file,'r') as f:
        for line in f:
            try:
                [ time, disk_used ] = line.split()
                # Add basic filter
                if len(time) != 10:
                    print >> sys.stderr,"invalid time format:",line
                    continue
        
                if more_detail:
                    d[strftime("%Y-%m-%d-%H", gmtime(int(time)))] = int(disk_used)/1024/1024
                else:
                    d[strftime("%Y-%m-%d", gmtime(int(time)))] = int(disk_used)/1024/1024
            except ValueError, error:
                print >> sys.stderr,"invalid input format:",line
    f.closed

    for key in sorted(d.keys()):
        if no_date:
            print d[key]
        else:
            print "{0} {1}".format(key,d[key])

if __name__ == "__main__":
    sys.exit(main())

