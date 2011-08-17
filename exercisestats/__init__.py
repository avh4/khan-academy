import operator
import itertools
import datetime
import math
import gc

from google.appengine.api import users
from mapreduce import control
from mapreduce import operation as op

from app import App
import request_handler
import models
import consts
import user_util

class Test(request_handler.RequestHandler):

    def get(self):
        problem_log_query = models.ProblemLog.all()
        problem_logs = problem_log_query.fetch(1000)

        problem_logs.sort(key=lambda log: log.time_taken)
        grouped = dict((k, sum(1 for i in v)) for (k, v) in itertools.groupby(problem_logs, key=lambda log: log.time_taken))

        hist = []
        total = sum(grouped[k] for k in grouped)
        cumulative = 0
        for time in range(180):
            count = grouped.get(time, 0)
            cumulative += count
            hist.append({
                "time": time,
                "count": count,
                "cumulative": cumulative,
                "percent": 100.0 * count / total,
                "percent_cumulative": 100.0 * cumulative / total,
                "percent_cumulative_tenth": 10.0 * cumulative / total,
            })

        context = { "selected_nav_link": "practice", "hist": hist, "total": total }

        self.render_template("exercisestats/test.html", context)

class GetFancyExerciseStatisticsTest(request_handler.RequestHandler):
    @user_util.developer_only
    def get(self):
        # Admin-only
        # mapreduce_id = control.start_map(
        #         name = "UpdateFancyExerciseStatistics",
        #         handler_spec = "exercisestats.fancy_statistics_update_map",
        #         reader_spec = "mapreduce.input_readers.DatastoreInputReader",
        #         reader_parameters = {"entity_kind": "models.Exercise"},
        #         queue_name = "fancy-exercise-statistics-mapreduce-queue",
        #         )
        # 
        # self.response.out.write("OK: " + str(mapreduce_id))

        self.response.headers.add_header("Content-Type", "text/plain")

        self.response.out.write("%s\n" % datetime.datetime.now())

        exid = self.request_string("exid")
        days = self.request_float("days", default = 1.0)
        delete = self.request_bool("delete", default = False)
        force_gc = self.request_bool("force_gc", default = False)
        gc_gen = self.request_int("gc_gen", default = -1)
        res = fancy_statistics_test(exid, days, delete, force_gc, gc_gen)

        self.response.out.write("%r\n" % (res,))
        self.response.out.write("%s\n" % datetime.datetime.now())

# fancy_statistics_update_map is called by a background MapReduce task.
# Each call updates the statistics for a single exercise.
def fancy_statistics_test(exid, days, delete, force_gc, gc_gen):
    
    query = models.ProblemLog.all()
    if len(exid) > 0:
        query.filter('exercise =', exid)
    query.filter('correct = ', True)
    query.filter('time_done >', datetime.datetime.now() - datetime.timedelta(days = days))
    query.order('-time_done')

    # { time_taken: frequency } pairs
    freq_table = {}
    total_count = 0

    # { time_taken: frequency } pairs for 3 < time_taken < consts.MAX_WORKING_ON_PROBLEM_SECONDS
    reasonable_freq_table = {}
    reasonable_count = 0

    while True:
        problem_logs = query.fetch(1000)

        if len(problem_logs) <= 0:
            break

        for problem_log in problem_logs:
            time = problem_log.time_taken

            freq_table[time] = 1 + freq_table.get(time, 0)
            total_count += 1

            if 3.0 < time < consts.MAX_WORKING_ON_PROBLEM_SECONDS:
                reasonable_freq_table[time] = 1 + reasonable_freq_table.get(time, 0)
                reasonable_count += 1

        query.with_cursor(query.cursor())

        if delete:
            del problem_logs
        if force_gc:
            if gc_gen >= 0:
                gc.collect(gc_gen)
            else:
                gc.collect()

    list_time_taken = []
    for time in sorted(reasonable_freq_table.keys()):
        # Cast to an int to (hopefully) save some memory over a long
        list_time_taken.extend([int(time)] * freq_table[time])

    fastest_percentile = percentile(list_time_taken, consts.FASTEST_EXERCISE_PERCENTILE)
    fastest_percentile = min(consts.MAX_SECONDS_PER_FAST_PROBLEM, fastest_percentile)
    fastest_percentile = max(consts.MIN_SECONDS_PER_FAST_PROBLEM, fastest_percentile)
    return (freq_table, list_time_taken, total_count, fastest_percentile)

# See http://code.activestate.com/recipes/511478-finding-the-percentile-of-the-values/
def percentile(N, percent, key=lambda x:x):
    """
    Find the percentile of a list of values.

    @parameter N - is a list of values. Note N MUST BE already sorted.
    @parameter percent - a float value from 0.0 to 1.0.
    @parameter key - optional key function to compute value from each element of N.

    @return - the percentile of the values
    """
    if not N:
        return None
    k = (len(N)-1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return key(N[int(k)])
    d0 = key(N[int(f)]) * (k-f)
    d1 = key(N[int(c)]) * (c-k)
    return d0+d1
