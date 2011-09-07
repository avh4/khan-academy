from __future__ import absolute_import

import layer_cache
import exercisestats.number_trivia as number_trivia
import request_handler
import user_util

from models import ProblemLog, Exercise
from .models import ExerciseStatistic

import bisect
import cgi
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

################################################################################

# Create a new list of KVPs with the values of all KVPs with identical keys summed
def sum_keys(key_value_pairs):
    histogram = {}
    for k, v in key_value_pairs:
        histogram[k] = histogram.get(k, 0) + v

    return list(histogram.items())

def to_unix_secs(date_and_time):
    return int(time.mktime(date_and_time.timetuple()))

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
    unix_secs = to_unix_secs(dt.datetime.now())
    ret = (unix_secs / refresh_secs) % bucket_size
    return ret

################################################################################

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
            start_unix = to_unix_secs(ex.start_dt) * 1000
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
        self.render_json(self.exercise_counter_for_geckoboard_rag())

    @staticmethod
    @layer_cache.cache(expiration=CACHE_EXPIRATION_SECS, layer=layer_cache.Layers.Memcache)
    def exercise_counter_for_geckoboard_rag():
        exercises = Exercise.get_all_use_cache()
        exercises.sort(key=lambda ex: ex.creation_date, reverse=True)

        last_exercise = exercises[-1]
        num_exercises = len(exercises)
        last_exercise_author = last_exercise.author.nickname() if last_exercise.author else 'random person'

        text = "Thanks %s for %s!" % (last_exercise_author, last_exercise.display_name)

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

class ExerciseNumberTrivia(request_handler.RequestHandler):
    def get(self):
        number = self.request_int('num', len(Exercise.get_all_use_cache()))
        self.render_json(self.number_facts_for_geckboard_text(number))

    # Not caching because there is no datastore access in this function
    @staticmethod
    def number_facts_for_geckboard_text(number):
        math_fact = number_trivia.math_facts.get(number,
            'This number is interesting. Why? Suppose there exists uninteresting '
            'natural numbers. Then the smallest in that set would be '
            'interesting by virtue of being the first: a contradiction. '
            'Thus all natural numbers are interesting.')
        year_fact = number_trivia.year_facts.get(number, 'nothing interesting happened')

        misc_fact_keys = sorted(number_trivia.misc_facts.keys())
        first_available_num = misc_fact_keys[bisect.bisect_left(misc_fact_keys, number) - 1]
        greater_than_fact = number_trivia.misc_facts[first_available_num]

        text1 = 'We now have more exercises than %s (%s)!' % (
            cgi.escape(greater_than_fact), str(first_available_num))
        text2 = math_fact
        text3 = "In year %d, %s." % (number, cgi.escape(year_fact))

        return {
            'item': [
                { 'text': text1 },
                { 'text': text2 },
                { 'text': text3 },
            ]
        }

class UserLocationsMap(request_handler.RequestHandler):
    def get(self):
        yesterday = dt.date.today() - dt.timedelta(days=1)
        date = self.request_date('date', "%Y/%m/%d", yesterday)

        self.render_json(self.get_ip_addresses_for_geckoboard_map(date))

    @staticmethod
    @layer_cache.cache_with_key_fxn(lambda date: str(date),
        expiration=CACHE_EXPIRATION_SECS, layer=layer_cache.Layers.Memcache)
    def get_ip_addresses_for_geckoboard_map(date):
        ip_addresses = []

        for ex in Exercise.get_all_use_cache():
            stat = ExerciseStatistic.get_by_date(ex.name, date)

            if stat:
                ip_addresses += stat.histogram.get('ip_addresses', [])

        return {
            'points': {
                'point': [{'ip': addr} for addr in ip_addresses]
            }
        }

class ExercisesCreatedHistogram(request_handler.RequestHandler):
    def get(self):
        past_days = self.request_int('past_days', 7)
        today_dt = dt.datetime.combine(dt.date.today(), dt.time())
        earliest_dt = today_dt- dt.timedelta(days=past_days)

        self.response.out.write(self.get_histogram_spline_for_highcharts(earliest_dt))

    @layer_cache.cache_with_key_fxn(lambda self, date: str(date),
        expiration=CACHE_EXPIRATION_SECS, layer=layer_cache.Layers.Memcache)
    def get_histogram_spline_for_highcharts(self, earliest_dt=dt.datetime.min):
        histogram = {}
        for ex in Exercise.get_all_use_cache():
            timestamp = to_unix_secs(ex.creation_date) * 1000 if ex.creation_date else 0
            histogram[timestamp] = histogram.get(timestamp, 0) + 1

        total_exercises = {}
        prev_value = 0
        for day, value in sorted(histogram.items()):
            prev_value = total_exercises[day] = prev_value + value

        # Only retain recent dates
        earliest_unix = to_unix_secs(earliest_dt) * 1000
        histogram = [[k,v] for k,v in histogram.items() if k >= earliest_unix]
        total_exercises = [[k,v] for k,v in total_exercises.items() if k >= earliest_unix]

        context = {
            'series': [
                {
                    'type': 'column',
                    'values': json.dumps(histogram),
                    'axis': 0,
                },
                {
                    'type': 'spline',
                    'values': json.dumps(total_exercises),
                    'axis': 1,
                }
            ],
            # Let highcharts determine the scales for now.
            'axes': [
                { 'max': 'null' },
                { 'max': 'null' },
            ],
        }

        return self.render_template_to_string(
            'exercisestats/highcharts_exercises_created_histogram.json', context)
