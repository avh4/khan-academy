from __future__ import absolute_import

import request_handler
import user_util

from google.appengine.ext import db
import copy
import logging

from itertools import groupby
from models import ProblemLog
from .models import ExerciseStatistic
import simplejson as json

import datetime as dt

# TODO: use cronjob with sharding, as in __init__.py
# TODO: fix up styling
# TODO: support specific date
# TODO: output in a generic JSON format, and use an adapter to convert to Geckoboard
# NOTE: Assumptions: cron job is run every day.
class Data(request_handler.RequestHandler):

    def get(self):
        exid = self.request_string('exid', 'addition_1')
        # Acceptable values are "done" and "proficient"
        hist = self.request_string('hist', 'done')

        today_dt = dt.datetime.combine(dt.date.today(), dt.time())
        tomorrow_dt = today_dt + dt.timedelta(days=1)
        start_dt = self.request_date('start_date', "%Y/%m/%d", today_dt)
        end_dt = self.request_date('end_date', "%Y/%m/%d", tomorrow_dt)

        query = ExerciseStatistic.all()
        query.filter('exid = ', exid)
        query.filter('start_dt >=', start_dt)
        query.order('start_dt')

        def num_proficient(ex):
            return sum(ex.histogram['proficiency_problem_number_frequencies'].values())

        def num_done(ex):
            return ex.log_count

        values = []
        num_func = { 'done': num_done, 'proficient': num_proficient }[hist]
        months = []
        for stat in query:
            # We can't just add another filter to the query because of GQL restrictions
            if (stat.end_dt > end_dt):
                logging.info('stat.end_dt =' + str(stat.end_dt) + ' end_dt =' + str(end_dt))
                continue
            values.append(num_func(stat))
            # TODO: a more efficient way of doing this would be to loop from
            #     start month to end month, which assumes cron job runs every day
            month = stat.start_dt.strftime('%b')
            if len(months) == 0 or month != months[-1]:
                months.append(month)

        axisy = [min(values), max(values)]
        gecko_dict = {
            'item': values,
            'settings': {
                'axisx': months,
                'axisy': axisy,
                'colour': 'ff9900',
            }
        }

        print 'Content-Type: text/plain'
        print
        print json.dumps(gecko_dict)

        # #return self.render_hist(ex.histogram[hist])
    
        # 
        # # TODO: if no date specified, spit out list for each day
        # yesterday = dt.date.today() - dt.timedelta(days=1)
        # yesterday_dt = dt.datetime.combine(yesterday, dt.time())
        # date = self.request_date('date', "%Y/%m/%d", yesterday_dt)
        # start_dt, end_dt = ExerciseStatistic.date_to_bounds(date)

        # bounds = ExerciseStatistic.date_to_bounds(date)

        # # TODO: There's gotta be a Python idiom for this, or at least a more generic way of doing this
        # def numUniqueUsers(query):
        #     users = set()
        #     for obj in query:
        #         users.add(obj.user)
        #     return len(users)

        # query = ProblemLog.all()
        # query.filter('exercise =', exid)

        # date_query = copy.deepcopy(query)
        # date_query.filter('time_done >=', start_dt)
        # date_query.filter('time_done <', end_dt)

        # stats = {}

        # # TODO: use our API methods instead of printing raw CGI
        # #print 'Content-Type: application/json'
        # print 'Content-Type: text/plain'
        # print ''
        # stats['numUsedTotal'] = numUniqueUsers(query)
        # query.filter('earned_proficiency =', True)
        # stats['numProficientTotal'] = numUniqueUsers(query)

        # stats['numUsedDate'] = numUniqueUsers(date_query)
        # # TODO: duplicate code
        # date_query.filter('earned_proficiency =', True)
        # stats['numProficientDate'] = numUniqueUsers(date_query)

        # print(str(stats))



#class Test(request_handler.RequestHandler):
#    @user_util.developer_only
#    def get(self):
#        return self.from_exercise_stats()
#
#    def from_exercise_stats(self):
#        hist = self.request_string('hist', 'time_taken_frequencies')
#       rexid = self.request_string('exid', 'addition_1')
#        date = self.request_string('date')
#
#        yesterday = dt.date.today() - dt.timedelta(days=1)
#        yesterday_dt = dt.datetime.combine(yesterday, dt.time())
#        date = self.request_date('date', "%Y/%m/%d", yesterday_dt)
#
#        bounds = ExerciseStatistic.date_to_bounds(date)
#        key_name = ExerciseStatistic.make_key(exid, bounds[0], bounds[1])
#        ex = ExerciseStatistic.get_by_key_name(key_name)
#        if not ex:
#            raise Exception("No ExerciseStatistic found with key_name %s", key_name)
#
#        return self.render_hist(ex.histogram[hist])
#
#    # only used for testing
#    def from_problem_logs(self):
#        problem_log_query = ProblemLog.all()
#        problem_logs = problem_log_query.fetch(1000)
#
#        problem_logs.sort(key=lambda log: log.time_taken)
#        grouped = dict((k, sum(1 for i in v)) for (k, v) in groupby(problem_logs, key=lambda log: log.time_taken))
#        return self.render_hist(grouped)
#
#    def render_hist(self, data):
#        max_t = min(180, max(data.keys()))
#        hist = []
#        total = sum(data[k] for k in data)
#        cumulative = 0
#        for time in range(max_t+2):
#            count = data.get(time, 0)
#            cumulative += count
#            hist.append({
#                'time': time,
#                'count': count,
#                'cumulative': cumulative,
#                'percent': 100.0 * count / total,
#                'percent_cumulative': 100.0 * cumulative / total,
#                'percent_cumulative_tenth': 10.0 * cumulative / total,
#            })
#
#        context = { 'selected_nav_link': 'practice', 'hist': hist, 'total': total }
#
#        self.render_template('exercisestats/test.html', context)
