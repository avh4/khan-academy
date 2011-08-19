from google.appengine.ext import db
from time import mktime


class ExerciseStatisticShard(db.Model):
    # key_name is "%s:%d:%d:%s" % (exid, unix_start, unix_end, cursor)
    exid = db.StringProperty(required=True)
    start_dt = db.DateTimeProperty(required=True)
    end_dt = db.DateTimeProperty(required=True)
    cursor = db.StringProperty()
    blob_val = db.BlobProperty()

    @staticmethod
    def make_key(exid, start_dt, end_dt, cursor):
        unix_start = int(mktime(start_dt.timetuple()))
        unix_end = int(mktime(end_dt.timetuple()))
        key_name = "%s:%d:%d:%s" % (exid, unix_start, unix_end, cursor)
        return key_name

class ExerciseStatistic(db.Model):
    # key_name is "%s:%d:%d" % (exid, unix_start, unix_end)
    exid = db.StringProperty(required=True)
    start_dt = db.DateTimeProperty(required=True)
    end_dt = db.DateTimeProperty(required=True)
    blob_val = db.BlobProperty(required=True)
    log_count = db.IntegerProperty(required=True)
    time_logged = db.DateTimeProperty(auto_now_add=True)

    @staticmethod
    def make_key(exid, start_dt, end_dt):
        unix_start = int(mktime(start_dt.timetuple()))
        unix_end = int(mktime(end_dt.timetuple()))
        key_name = "%s:%d:%d" % (exid, unix_start, unix_end)
        return key_name
