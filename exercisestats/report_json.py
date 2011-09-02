from __future__ import absolute_import

import request_handler
import user_util

from models import ProblemLog, Exercise
from .models import ExerciseStatistic

import datetime as dt
import math
import random
import time
import simplejson as json

# Constants for Geckoboard display.
NUM_BUCKETS = 20
PAST_DAYS_TO_SHOW = 7

# Create a new list of KVPs with the values of all KVPs with identical keys summed
def sum_keys(key_value_pairs):
    key_value_pairs.sort()
    ret = []
    last = None
    for k, v in key_value_pairs:
        if last == None or last != k:
            ret.append([k, v])
            last = k
        else:
            ret[-1][1] += v
    return ret

def exercises_in_bucket(num_buckets, bucket_index):
    exercise_names = [ex.name for ex in Exercise.get_all_use_cache()]
    exercise_names.sort()

    # These calculations evenly distribute exercises among buckets, with excess
    # going to the first few buckets.
    # In particular, max_capcity(buckets) - min_capacity(buckets) <= 1.
    bucket_size = len(exercise_names) / num_buckets
    bucket_rem = len(exercise_names) % num_buckets
    first = bucket_index * bucket_size + min(bucket_rem, bucket_index)
    return exercise_names[ first : first + bucket_size + (1 if bucket_index < bucket_rem else 0) ]

class ExerciseDoneProfGraph(request_handler.RequestHandler):
    def get(self):
        chart = self.request_string('chart', 'area_spline')

        past_days = self.request_int('past_days', 7)
        today = dt.date.today()
        # We don't use App Engine Query filters so as to avoid adding entries to index.yaml
        days = [ today - dt.timedelta(days=i) for i in range(past_days - 1, -1, -1) ]

        if chart == 'aggregate':
            # For-loop for clarity and to get flattened list (over list comp.)
            ex_stats = []
            for ex in Exercise.get_all_use_cache():
                ex_stats += ExerciseStatistic.get_by_dates(ex.name, days)

            return self.area_spline(ex_stats, 'All Exercises')

        num_buckets = self.request_int('n', 1)
        bucket_index = self.request_int('ix', 0)
        exercise_names = self.request_string('exercise_names', '')

        exercise_names = [e for e in exercise_names.split(',') if e]
        if not exercise_names:
            exercise_names = exercises_in_bucket(num_buckets, bucket_index)

        exid = random.choice(exercise_names)
        ex_stats = ExerciseStatistic.get_by_dates(exid, days)

        return { 'gecko_line': self.gecko_line,
                 'area_spline': self.area_spline }[chart](ex_stats, exid)

    def area_spline(self, exercise_stats, title=''):
        prof_list, done_list = [], []
        for ex in exercise_stats:
            start_unix = int(time.mktime(ex.start_dt.timetuple()) * 1000)
            prof_list.append([start_unix, ex.num_proficient()])
            done_list.append([start_unix, ex.num_problems_done()])

        done_list = sum_keys(done_list)
        prof_list = sum_keys(prof_list)

        title = Exercise.to_display_name(title)

        # Make the peak of the proficiency line about half as high as the peak
        # of the # problems graph
        done_y_max = max([x[1] for x in done_list]) if len(done_list) else 1
        prof_y_max = max([x[1] for x in prof_list]) * 2 if len(prof_list) else 1

        context = {
            'title': title,
            'series1': {
                'name': 'Problems Done', 
                'max': done_y_max,
                'values': json.dumps(done_list),
            },
            'series2': {
                'name': 'Proficient',
                'max': prof_y_max,
                'values': json.dumps(prof_list),
            },
        }

        self.render_template('exercisestats/highcharts_area_spline.json', context)

    def gecko_line(self, exercise_stats, title):
        # Acceptable values are "done" and "proficient"
        hist = self.request_string('hist', 'done')

        values, months = [], []
        num_func = { 'done': ExerciseStatistic.num_problems_done,
                     'proficient': ExerciseStatistic.num_proficient }[hist]

        for ex in exercise_stats:
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
        return self.redirect('/exercisestats/json?chart=area_spline&past_days=%d&n=%d&ix=%d'
            % (PAST_DAYS_TO_SHOW, NUM_BUCKETS, bucket_index))
