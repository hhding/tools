#!/usr/bin/env python

import gevent
import sys
from gevent.server import StreamServer  
from gevent.socket import create_connection, gethostbyname  
import traceback  
import logging
import logging.handlers

from optparse import OptionParser

class ForwardNode(StreamServer):
    global logger
    def config_forward(self, remote_ip, remote_port):
        self.remote_ip = remote_ip
        self.remote_port = remote_port

    def handle(self, client, address):
        ip, port = client.getpeername()[:2]
        logger.info("Connecting from: %s:%s" % (ip, port))
        try:
            remote = create_connection((self.remote_ip, self.remote_port))
        except:
            logger.warn("faild to make connection to %s:%s" % (self.remote_ip, self.remote_port))
            client.close()
            traceback.print_exc()  
        else:
            gevent.spawn(forward, client, remote)
            gevent.spawn(forward, remote, client)

def forward(src, dst):
    try:
        while True:
            data = src.recv(4096)
            # as blocking IO, no data means the connection is closed
            # still possible half shutdown tcp connections
            if not data:
                break
            dst.sendall(data)
    except:
        pass
    finally:
        src.close()
        dst.close()

options = OptionParser(description='Port forwarding application')
options.add_option("-s", "--src", dest="src", default='0.0.0.0:1984', help="bind_ip:port")  
options.add_option("-d", "--dst", dest="dst",  help="forward_ip:port")  
logger = logging.getLogger("pyPF")
logger.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(address = '/dev/log')
f = logging.Formatter('pyPF: %(message)s')
handler.setFormatter(f)
logger.addHandler(handler)

def main():
    opts, args = options.parse_args()
    if not opts.dst:
        options.print_help()
        return

    try:
        remote_host, remote_port = opts.dst.split(":")
        remote_ip = gethostbyname(remote_host)
        local_ip, local_port = opts.src.split(":")
    except:
        options.print_help()
        return

    server = ForwardNode((local_ip, int(local_port)))
    server.config_forward(remote_ip, remote_port)
    logger.info("listening at %s" % local_port)
    server.start()
    server.serve_forever()

if __name__ == '__main__':  
    main()  

