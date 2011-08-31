from __future__ import absolute_import

import request_handler
import user_util

from models import ProblemLog, Exercise
from .models import ExerciseStatistic

import datetime as dt
import time

# NOTE: Assumptions: Collect Fancy Exercise Statistics cron job is run everyday.
class Data(request_handler.RequestHandler):
    #@user_util.developer_only
    def get(self):
        chart = self.request_string('chart', 'gecko_line')
        exid = self.request_string('exid', 'addition_1')

        today_dt = dt.datetime.combine(dt.date.today(), dt.time())
        tomorrow_dt = today_dt + dt.timedelta(days=1)
        start_dt = self.request_date('start_date', "%Y/%m/%d", today_dt)
        end_dt = self.request_date('end_date', "%Y/%m/%d", tomorrow_dt)

        query = ExerciseStatistic.all()
        query.filter('exid = ', exid)
        query.filter('start_dt >=', start_dt)
        query.order('start_dt')

        # TODO: Instead of passing a query and end_dt, pass in an
        #     iterable/generator that automatically omits end_dt
        return { 'gecko_line': self.gecko_line,
                 'area_spline': self.area_spline }[chart](exid, query, end_dt)

    def area_spline(self, exid, stat_query, end_dt):
        prof_list, done_list = [], []
        start_ts = 0
        for ex in stat_query:

            if (ex.end_dt > end_dt):
                continue

            if not start_ts:
                start_ts = int(time.mktime(ex.start_dt.timetuple()) * 1000)

            prof_list.append(ex.num_proficient())
            done_list.append(ex.num_problems_done())

        title = Exercise.to_display_name(exid)
        # TODO: This is just a quick hack to ensure the proficiency area does not mask the # done area
        prof_y_max = max(prof_list) * 2

        context = {
            'title': title,
            'series1': {
                'name': 'Problems Done', 
                'max': 'null',
                'values': done_list,
            },
            'series2': {
                'name': 'Proficient',
                'max': prof_y_max,
                'values': prof_list,
            },
            'start_ts': start_ts,
            'interval': 24 * 60 * 60 * 1000,
        }

        self.render_template('exercisestats/highcharts_area_spline.json', context)

    def gecko_line(self, exid, stat_query, end_dt):
        # Acceptable values are "done" and "proficient"
        hist = self.request_string('hist', 'done')

        values, months = [], []
        num_func = { 'done': ExerciseStatistic.num_problems_done,
                     'proficient': ExerciseStatistic.num_proficient }[hist]
        for ex in stat_query:
            # We can't just add another filter to the query because of GQL restrictions
            if (ex.end_dt > end_dt):
                continue
            values.append(num_func(ex))
            # TODO: a more efficient way of doing this would be to loop from
            #     start month to end month, which assumes cron job runs every day
            month = ex.start_dt.strftime('%b')
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

        self.render_json(gecko_dict)
