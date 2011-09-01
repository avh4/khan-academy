from __future__ import absolute_import

import request_handler
import user_util

from models import ProblemLog, Exercise
from .models import ExerciseStatistic

import datetime as dt
import math
import random
import time
import logging

def exercises_in_bucket(num_buckets, bucket_index):
    # TODO: Optimization: Don't re-calculate exercise data each time
    exercises = [e.name for e in Exercise.get_all_use_cache()]
    exercises.sort()

    # These calculations evenly distribute exercises among buckets, with excess
    # going to the first few buckets.
    # In particular, max_capcity(buckets) - min_capacity(buckets) <= 1.
    bucket_size = len(exercises) / num_buckets
    bucket_rem = len(exercises) % num_buckets
    first = bucket_index * bucket_size + min(bucket_rem, bucket_index)
    return exercises[ first : first + bucket_size + (1 if bucket_index < bucket_rem else 0) ]

# NOTE: Assumptions: Collect Fancy Exercise Statistics cron job is run everyday.
class ExerciseDoneProfGraph(request_handler.RequestHandler):
    def get(self):
        chart = self.request_string('chart', 'gecko_line')

        past_days = self.request_int('past_days', 7)
        end_dt = dt.datetime.combine(dt.date.today(), dt.time()) + dt.timedelta(days=1)
        start_dt = end_dt - dt.timedelta(days=past_days)

        query = ExerciseStatistic.all()
        query.filter('start_dt >=', start_dt)
        query.order('start_dt')

        if chart == 'aggregate':
            return self.area_spline(query, end_dt, 'All Exercises')

        num_buckets = self.request_int('n', 1)
        bucket_index = self.request_int('ix', 0)
        exercises = self.request_string('exercises', '')
        exercises = [e for e in exercises.split(',') if e]
        if not exercises:
            exercises = exercises_in_bucket(num_buckets, bucket_index)
        exid = random.choice(exercises)
        query.filter('exid = ', exid)

        return { 'gecko_line': self.gecko_line,
                 'area_spline': self.area_spline }[chart](query, end_dt, exid)

    def area_spline(self, stat_query, end_dt, title=''):
        prof_list, done_list = [], []
        start_ts = 0

        for ex in stat_query:
            if (ex.end_dt > end_dt):
                continue

            if not start_ts:
                start_ts = int(time.mktime(ex.start_dt.timetuple()) * 1000)

            prof_list.append(ex.num_proficient())
            done_list.append(ex.num_problems_done())

        title = Exercise.to_display_name(title)

        # Make the peak of the proficiency line about half as high as the peak
        # of the # problems graph
        done_y_max = max(done_list) if len(done_list) else 1
        prof_y_max = max(prof_list) * 2 if len(prof_list) else 1

        context = {
            'title': title,
            'series1': {
                'name': 'Problems Done', 
                'max': done_y_max,
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

    def gecko_line(self, stat_query, end_dt, title):
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
            month = ex.start_dt.strftime('%b')
            if len(months) == 0 or month != months[-1]:
                months.append(month)

        axisy = [min(values), max(values)] if len(values) else [0, 1]
        gecko_dict = {
            'item': values,
            'settings': {
                'axisx': months,
                'axisy': axisy,
                'colour': 'ff9900',
            }
        }

        self.render_json(gecko_dict)

# This redirect is to eliminate duplicate code so we don't have to change every
# Geckoboard widget's URL for a general change
class GeckoboardExercisesRedirect(request_handler.RequestHandler):
    def get(self):
        bucket_index = self.request_int('ix', 0)
        return self.redirect('/exercisestats/json?chart=area_spline&past_days=7&n=20&ix=%d' % bucket_index)
