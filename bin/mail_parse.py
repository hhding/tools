#!/usr/bin/python

import logging
import sys

def decode_header(header):
    s = ""
    for (c,e) in header:
        if e is None:
            c_utf8 = c.encode('utf-8')
        else:
            c_utf8 = c.decode(e).encode('utf-8')
        s = s + c_utf8
    return s   

def main():
    logger = logging.getLogger("root")

    data = open(sys.argv[1]).read()

    import email
    import email.parser
    header = email.parser.Parser().parsestr(data)
    
    #logger.info( "=================== Process mail %s =================" % uidl)
    s = email.Header.decode_header(header['subject']) 
    f = email.Header.decode_header(header['from']) 
    print "From: %s" % decode_header(f), "Subject: %s" % decode_header(s)
    #print "Subject: %s" % header['subject']
    logger.info( "Subject: %s" % header['subject'])
    logger.info( "Sender: %s" % header['sender'])
    logger.info( "From: %s" % header['from'])


if __name__ == '__main__':
    main()

