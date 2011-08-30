from __future__ import absolute_import

import request_handler
import user_util

from models import ProblemLog, Exercise
from .models import ExerciseStatistic

import datetime as dt
import time

# NOTE: Assumptions: cron job is run everyday.
class Data(request_handler.RequestHandler):
    @user_util.developer_only
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

    @staticmethod
    def num_proficient(ex):
        return sum(ex.histogram['proficiency_problem_number_frequencies'].values())

    @staticmethod
    def num_done(ex):
        return ex.log_count

    def area_spline(self, exid, stat_query, end_dt):
        prof_list, done_list = [], []
        start_ts = 0
        for ex in stat_query:
            if (ex.end_dt > end_dt):
                continue
            if not start_ts:
                start_ts = int(time.mktime(ex.start_dt.timetuple()) * 1000)
            prof_list.append(Data.num_proficient(ex))
            done_list.append(Data.num_done(ex))

        title = Exercise.to_display_name(exid)

        # TODO: load this data from a template or file or something
        data = {
            'chart': {
                'renderTo': 'container',
                'plotBackgroundColor': 'rgba(35,37,38,0)',
                'backgroundColor': 'rgba(35,37,38,100)',
                'borderColor': 'rgba(35,37,38,100)',
                'lineColor': 'rgba(35,37,38,100)',
                'plotBorderColor': 'rgba(35,37,38,100)',
                'plotBorderWidth': None,
                'plotShadow': False,
                'height': 340,
                'type': 'areaspline',
            },
            'colors': [ '#058DC7', '#50B432', '#EF561A' ],
            'credits': { 'enabled': False },
            'title': { 'text': title },
            'legend': {
                'borderColor': 'rgba(35,37,38,100)',
                'margin': 5,
            },
            'plotOptions': {
                'areaspline': {
                    'dataLabels': { 'enabled': False },
                    'showInLegend': True,
                    'size': '100%',
                },
            },
            'series': [
                {
                    'data': done_list,
                    'name': 'Done',
                    'pointStart': start_ts,
                    'pointInterval': 24 * 3600 * 1000,
                },
                {
                    'data': prof_list,
                    'name': 'Proficient',
                    'pointStart': start_ts,
                    'pointInterval': 24 * 3600 * 1000,
                },
            ],
            'yAxis': { 'title': None },
            'xAxis': { 'type': 'datetime' },
        }

        self.render_json(data)

    def gecko_line(self, exid, stat_query, end_dt):
        # Acceptable values are "done" and "proficient"
        hist = self.request_string('hist', 'done')

        values, months = [], []
        num_func = { 'done': Data.num_done, 'proficient': Data.num_proficient }[hist]
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

        print self.render_json(gecko_dict)
