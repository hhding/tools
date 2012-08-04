from time import gmtime, strftime
import pytz

class TimeConvertor:
    def __init__(self,tz="Asia/Shanghai"):
        self.tz = pytz.timezone (tz)
        pass

    def to_readable(self,time,fmt="%Y-%m %d:%H:%M"):
        return strftime(fmt, gmtime(int(time)))
