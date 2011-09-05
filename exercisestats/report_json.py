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
    for k, v in key_value_pairs:
        histogram[k] = histogram.get(k, 0) + v

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
        prof_list, done_list, new_users_list = [], [], []
        for ex in exercise_stats:
            start_unix = int(time.mktime(ex.start_dt.timetuple()) * 1000)
            prof_list.append([start_unix, ex.num_proficient()])
            done_list.append([start_unix, ex.num_problems_done()])
            new_users_list.append([start_unix, ex.num_new_users()])

        # It's possible that the ExerciseStats that we go through has multiple
        # entries for a particular day (eg. if we were aggregating more than
        # one exercise). Sum them.
        done_list = sum_keys(done_list)
        prof_list = sum_keys(prof_list)
        new_users_list = sum_keys(new_users_list)

        title = Exercise.to_display_name(title)

        # Make the peak of the new users and proficiency series about half as
        # high as the peak of the # problems line
        left_axis_max = max([x[1] for x in done_list]) if done_list else 1
        right_axis_max = max([x[1] for x in new_users_list]) * 2 if new_users_list else 1

        context = {
            'title': title,
            'series': [
                {
                    'name': 'Problems Done',
                    'values': json.dumps(done_list),
                    'axis': 0,
                },
                {
                    'name': 'Proficient',
                    'values': json.dumps(prof_list),
                    'axis': 1,
                },
                {
                    'name': 'New users',
                    'values': json.dumps(new_users_list),
                    'axis': 1,
                },
            ],
            'axes': [
                { 'max': left_axis_max },
                { 'max': right_axis_max },
            ],
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


# TODO: Either allow returning graphs for other statistics, such as #
#     proficient, or somehow display more statistics on the same graph nicely
class ExerciseStatsMapGraph(request_handler.RequestHandler):
    # TODO: Just move this logic into get and make get_use_cache take a day parameter.
    def get_request_params(self):
        yesterday = dt.date.today() - dt.timedelta(days=1)
        interested_day = self.request_date('date', "%Y/%m/%d", yesterday)

        return {
            'interested_day': interested_day
        }

    def get(self):
        self.response.out.write(self.get_use_cache())

    @layer_cache.cache_with_key_fxn(lambda self: str(self.get_request_params()),
        expiration=CACHE_EXPIRATION_SECS, layer=layer_cache.Layers.Memcache)
    def get_use_cache(self):
        params = self.get_request_params()

        # Get the maximum so we know how the data label circles should be scaled
        most_new_users = 1
        ex_stat_dict = {}
        for ex in Exercise.get_all_use_cache():
            stat = ExerciseStatistic.get_by_date(ex.name, params['interested_day'])
            ex_stat_dict[ex.name] = stat
            if stat:
                most_done = max(most_new_users, stat.num_new_users())

        data_points = []
        for ex in Exercise.get_all_use_cache():
            stat = ex_stat_dict[ex.name]

            # The exercise map is rotated 90 degrees because we can fit more on
            # Geckoboard's tiny 2x2 widget that way.
            x, y = int(ex.h_position), int(ex.v_position)

            # Set the area of the circle proportional to the data value
            radius = 1
            if stat:
                radius = math.sqrt(float(stat.num_new_users()) / most_done) * MAX_POINT_RADIUS

            point = {
                'x': x,
                'y': y,
                'name': ex.display_name,
                'marker': {
                    'radius': max(radius, 1)
                },
            }
            data_points.append(point)

        context = {
            'title': 'Exercises Map',
            'series': {
                'name': 'New Users',
                'values': json.dumps(data_points),
            },
        }

        return self.render_template_to_string(
            'exercisestats/highcharts_scatter_map.json', context)

class ExercisesLastAuthorCounter(request_handler.RequestHandler):
    def get(self):
        self.render_json(self.geckoboard_rag_response())

    @layer_cache.cache(expiration=CACHE_EXPIRATION_SECS, layer=layer_cache.Layers.Memcache)
    def geckoboard_rag_response(self):
        exercises = Exercise.get_all_use_cache()
        # TODO: Last_modified field seems to be none (at least locally). Sort
        #     by another field, or actually use last_modified and author fields.
        exercises.sort(key=lambda ex: ex.last_modified)

        last_exercise = exercises[-1]
        num_exercises = len(exercises)

        text = "Thanks %s for %s!" % (
            last_exercise.author.nickname(), last_exercise.display_name)

        return {
            'item': [
                {
                    'value': None,
                    'text': '',
                },
                {
                    'value': None,
                    'text': '',
                },
                {
                    'value': num_exercises,
                    'text': text,
                },
            ]
        }
