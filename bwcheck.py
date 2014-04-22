#!/usr/bin/python

#import yaml
import socket
import sys
import os
import shlex
import logging
import logging.handlers
import time

from subprocess import Popen, PIPE

BIN_PATH=os.path.abspath(__file__)

#def load_proxy(file_path):
#    return yaml.load(open(file_path))

class Graphite(object):
    def __init__(self, addr='206.99.94.252', port=2003):
        self.addr = addr
        self.port = port

    def send(self, msg):
        now = int(time.time())
        from socket import socket,AF_INET,SOCK_DGRAM
        sock = socket(AF_INET, SOCK_DGRAM)
        message = "%s %d\n" % (msg, now)
        sock.sendto(message, (self.addr, self.port))

g = Graphite()

logger = logging.getLogger('proxy_check')

def setup_logging(target):
    fileHandler = logging.handlers.RotatingFileHandler(os.path.join(os.path.dirname(BIN_PATH),'%s.log' % target), mode='a', maxBytes=1000000, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    logger.setLevel(logging.DEBUG)

def check_proxy(url, target, timeout=30):
    global g
    cmd_base = 'curl -s -w "%{http_code} %{http_connect} %{time_total} %{time_namelookup} %{time_connect} %{time_appconnect} %{time_pretransfer} %{time_redirect} %{time_starttransfer}" -o /dev/null' 

    cmd_prefix = shlex.split(cmd_base)
    cmd = cmd_prefix + ['-m', "%s" % timeout, url]
    try:
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout = p.communicate()[0]
        stdout_break_down = stdout.split()
        http_code = stdout_break_down[0]
        time_total = stdout_break_down[2]
        return_code = p.returncode
        logger.info("%s %s" % (stdout, return_code))
        metrics = "network.dl.%s.%s" % (target, socket.gethostname())
        g.send("%s %s" % (metrics, time_total))
    except:
        pass

def main():
    target = sys.argv[1]
    url = sys.argv[2]
    setup_logging(target)
    while True:
        start_time = time.time()
        check_proxy(url, target, timeout = 59)
        elapsed = time.time() - start_time
        time.sleep(60-elapsed-0.1)

if __name__ == '__main__':
    main()

