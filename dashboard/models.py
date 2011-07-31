import datetime

from google.appengine.ext import db
from google.appengine.ext.db import stats

from counters import user_counter

# TODO: backfill just a couple weeks of problemlog counts
# TODO: hook up graphs
# TODO: test stats in production
# TODO: test cron

class DailyStatisticLog(db.Model):
    val = db.IntegerProperty(required=True, default=0)
    dt = db.DateTimeProperty(auto_now_add=True)
    stat_name = db.StringProperty(required=True)

class DailyStatistic(object):

    def calc(self):
        raise Exception("Not implemented")
    
    def record(self, val = None, dt = None):

        # Use subclass name as stat identifier
        stat_name = self.__class__.__name__

        if stat_name == DailyStatistic.__name__:
            raise Exception("Not implemented")

        if val is None:
            # Grab actual stat value, implemented by subclass
            val = self.calc()

        if dt is None:
            dt = datetime.datetime.now()

        if not val is None:

            # Use stat name and date (w/ hours/secs/mins stripped) as keyname so we don't record
            # duplicate stats
            key_name = "%s:%s" % (stat_name, dt.date().isoformat())

            return DailyStatisticLog.get_or_insert(
                    key_name = key_name,
                    stat_name = stat_name,
                    val = val,
                    dt = dt,
                    )

        return None

    @staticmethod
    def record_all():

        dt = datetime.datetime.now()

        # Record stats for all implementing subclasses
        for subclass in DailyStatistic.__subclasses__():
            instance = subclass()
            instance.record(dt)

class ProblemLogCount(DailyStatistic):

    def calc(self):
        kind_stat = stats.KindStat.all().filter("kind_name =", "ProblemLog")

        if kind_stat:
            return kind_stat.count()

        return None

class RegisteredUserCount(DailyStatistic):

    def calc(self):
        return user_counter.get_count()

