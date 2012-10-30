#!/usr/bin/python

from sqlalchemy import *
from sqlalchemy.orm import mapper
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relation, backref
#from sqlalchemy.orm import relationship, backref
from subprocess import Popen, PIPE
from datetime import datetime
import time
import os
import re

"""
mysql> select * from storageAttribute limit 2;
+----+------------+-------------------------------------------------+------------+-------------+
| id | host_name  | host_usage                                      | capability | data_center |
+----+------------+-------------------------------------------------+------------+-------------+
| 11 | nas-hz-01  | VTWeb(JPEG/GIF/DNA/FLV)  & Taisan(JPEG/GIF/DNA) |  10844.120 | WASU        |
| 12 | nas-hz-02  | Taisan(sn/msn)/MediaWise/vddb                   |  10833.920 | WASU        |
+----+------------+-------------------------------------------------+------------+-------------+
8 rows in set (0.00 sec)

mysql> select * from storage limit 2;
+----+---------------------+------------+------------+---------------------+
| id | storageAttribute_id | used_space | free_space | create_at           |
+----+---------------------+------------+------------+---------------------+
|  4 |                   6 |   6815.000 |   2261.000 | 2010-06-12 04:47:45 |
| 12 |                  13 |   2080.000 |    839.000 | 2010-06-12 04:52:53 |
+----+---------------------+------------+------------+---------------------+


"""
class MyError(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)

# These are the empty classes that will become our data classes
class Storage(object):
    pass

class StorageAttribute(object):
    pass

def setup_orm():
    engine = create_engine('mysql://user:pass@localhost/db',pool_size=2, max_overflow=0)
    metadata = MetaData(engine)
    storageattribute_table = Table('storageAttribute', metadata, autoload=True)
    storage_table = Table('storage', metadata, ForeignKeyConstraint(['storageAttribute_id'], ['storageAttribute.id']), autoload=True)

    mapper(Storage, storage_table,
        properties={
            'storage_attr': relation(StorageAttribute)
            }
        )
    mapper(StorageAttribute, storageattribute_table )

    return sessionmaker(bind=engine)

def process_one_snmp(one_line_data):
    data = one_line_data.split()[-1]
    data = re.sub("\"","",data)
    if data.endswith("T"):
        return float(data[:-1])*1024
    if data.endswith("G"):
        return float(data[:-1])
    if data.endswith("M"):
        return 0.0

    raise MyError("Not Valid data: %s" % one_line_data)

def get_snmp_data(host, uoid, foid):    
    cmdline = "snmpget -v2c -c public %s %s %s" % ( host, uoid, foid)
    #cmdline = "snmpget -v2c -c public %s UCD-SNMP-MIB::extOutput.1 UCD-SNMP-MIB::extOutput.2" % host
    process = Popen(cmdline.split(), shell = False, stdout = PIPE, stderr = PIPE)
    ret = process.wait()
    (output, errmsg) = process.communicate()
    if ret != 0:
        msg = "Error fetch snmp data: %s" % cmdline
        raise MyError(msg)

    snmp_info = output.splitlines()
    return map(process_one_snmp, snmp_info)

def main():

    nas_list = ['nas-hz-01','nas-hz-02']

    Session = setup_orm()
    session = Session()

    for nas_label in nas_list:
        attr = session.query(StorageAttribute).filter_by(host_name = nas_label).one()
        try:
            snmp_data = get_snmp_data(nas_label, '.1.3.6.1.4.1.2021.8.1.101.1', '.1.3.6.1.4.1.2021.8.1.101.2')
            ( used, free ) = snmp_data
        except MyError, inst:
            print inst.msg
        except Exception, e:
            # in case do not get the data
            msg = "unknown exception: type: %s, args: %s",type(e),e.args
            print msg
        else:
            os.environ['TZ'] = "America/Los_Angeles"
            fmt = "%Y-%m-%d %H:%M:%S"
            tztime_str = "%s" % time.strftime(fmt)
            now = datetime.strptime(tztime_str, fmt)
            s = Storage()
            s.storage_attr = attr
            s.used_space = used
            s.free_space = free
            s.create_at = now
            print s.storage_attr.host_name, s.create_at
            session.add(s)
            session.commit()

if __name__ == '__main__':
    main()
