from __future__ import absolute_import

import layer_cache
import request_handler
import user_util

from models import ProblemLog, Exercise
from .models import ExerciseStatistic

import datetime as dt
import math
import random
import time
import simplejson as json

import logging

# Constants for Geckoboard display.
NUM_BUCKETS = 20
PAST_DAYS_TO_SHOW = 7
REFRESH_SECS = 30

CACHE_EXPIRATION_SECS = 60 * 60

# For a point on the exercise map
MAX_POINT_RADIUS = 10

# Create a new list of KVPs with the values of all KVPs with identical keys summed
def sum_keys(key_value_pairs):
    histogram = {}
    for key, value in key_value_pairs:
        cur_val = histogram.get(key, 0)
        histogram[key] = cur_val + value

    return list(histogram.items())

def exercises_in_bucket(num_buckets, bucket_index):
    exercise_names = [ex.name for ex in Exercise.get_all_use_cache()]
    exercise_names.sort()

    # These calculations evenly distribute exercises among buckets, with excess
    # going to the first few buckets.
    # In particular, max_capacity(buckets) - min_capacity(buckets) <= 1.
    num_exercises = len(exercise_names)
    min_bucket_size = num_exercises / num_buckets
    bucket_rem = num_exercises % num_buckets

    first = bucket_index * min_bucket_size + min(bucket_rem, bucket_index)
    return exercise_names[ first : first + get_bucket_size(num_buckets, bucket_index) ]

def get_bucket_size(num_buckets, bucket_index):
    num_exercises = len(Exercise.get_all_use_cache())
    bucket_rem = num_exercises % num_buckets
    return (num_exercises / num_buckets) + (1 if bucket_index < bucket_rem else 0)

# Choose the exercise based on the time, so we can cycle predictably and also
# use the cache
def get_bucket_cursor(refresh_secs, bucket_size):
    unix_secs = int( time.mktime(dt.datetime.now().timetuple()) )
    ret = (unix_secs / refresh_secs) % bucket_size
    return ret

class ExerciseOverTimeGraph(request_handler.RequestHandler):
    def get_request_params(self):
        chart = self.request_string('chart', 'area_spline')
        past_days = self.request_int('past_days', 7)
        num_buckets = self.request_int('n', 1)
        bucket_index = self.request_int('ix', 0)
        refresh_secs = self.request_int('rsecs', 30)

        bucket_size = get_bucket_size(num_buckets, bucket_index)
        bucket_cursor = get_bucket_cursor(refresh_secs, bucket_size)

        return {
            'chart': chart,
            'past_days': past_days,
            'num_buckets': num_buckets,
            'bucket_index': bucket_index,
            'bucket_cursor': bucket_cursor,
        }

    def get_cache_key(self):
        params = self.get_request_params()

        if (params['chart'] == 'aggregate'):
            return "%s|%d" % (params['chart'], params['past_days'])

        return "%s|%d|%d|%d|%d" % (params['chart'], params['past_days'],
            params['num_buckets'], params['bucket_index'], params['bucket_cursor'])

    def get(self):
        self.response.out.write(self.get_use_cache())

    @layer_cache.cache_with_key_fxn(get_cache_key,
        expiration=CACHE_EXPIRATION_SECS, layer=layer_cache.Layers.Memcache)
    def get_use_cache(self):
        params = self.get_request_params()

        today = dt.date.today()
        # We don't use App Engine Query filters so as to avoid adding entries to index.yaml
        days = [ today - dt.timedelta(days=i) for i in range(0, params['past_days']) ]

        if params['chart'] == 'aggregate':
            # For-loop for clarity and to get flattened list (over list comp.)
            ex_stats = []
            for ex in Exercise.get_all_use_cache():
                ex_stats += ExerciseStatistic.get_by_dates(ex.name, days)

            return self.area_spline(ex_stats, 'All Exercises')

        exercise_names = exercises_in_bucket(params['num_buckets'], params['bucket_index'])

        exid = exercise_names[params['bucket_cursor']]
        ex_stats = ExerciseStatistic.get_by_dates(exid, days)

        return self.area_spline(ex_stats, exid)

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

        return self.render_template_to_string(
            'exercisestats/highcharts_area_spline.json', context)

# This redirect is to eliminate duplicate code so we don't have to change every
# Geckoboard widgets' URL for a general change
class GeckoboardExerciseRedirect(request_handler.RequestHandler):
    def get(self):
        bucket_index = self.request_int('ix', 0)
        return self.redirect('/exercisestats/exerciseovertime?chart=area_spline&past_days=%d&rsecs=%d&n=%d&ix=%d'
            % (PAST_DAYS_TO_SHOW, REFRESH_SECS, NUM_BUCKETS, bucket_index))

# Castro roulette
# We now have more exercises than x. Last exercise developer was X

# TODO: caching 
class ExerciseStatsMapGraph(request_handler.RequestHandler):

    def get(self):
        yesterday = dt.date.today() - dt.timedelta(days=3)

        most_done = 1
        ex_stat_dict = {}
        for ex in Exercise.get_all_use_cache():
            stat = ExerciseStatistic.get_by_date(ex.name, yesterday)
            ex_stat_dict[ex.name] = stat
            if stat:
                most_done = max(most_done, stat.num_problems_done())

        done_coords, prof_coords = [], []
        for ex in Exercise.get_all_use_cache():
            stat = ex_stat_dict[ex.name]
            x, y = int(ex.h_position), int(ex.v_position)
            radius = 1
            if stat:
                radius = math.sqrt(float(stat.num_problems_done()) / most_done) * MAX_POINT_RADIUS

            point = {
                'x': x,
                'y': y,
                'name': ex.display_name,
                'marker': {
                    'radius': max(radius, 1)
                }
            }
            done_coords.append(point)
            #prof_coords.append([x, y])

        context = {
            'title': 'Exercises Map',
            'series1': {
                'name': 'Problems Done',
                'values': json.dumps(done_coords),
            },
            'series2': {
                'name': 'Proficient',
                'values': json.dumps(prof_coords),
            },
        }

        self.render_template('exercisestats/highcharts_scatter_map.json', context)
