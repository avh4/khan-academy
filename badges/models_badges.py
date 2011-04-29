#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime

from google.appengine.ext import db

class BadgeStat(db.Model):
    badge_name = db.StringProperty()
    count_awarded = db.IntegerProperty(default = 0)
    dt_last_calculated = db.DateTimeProperty(auto_now_add=True)

    @staticmethod
    def get_or_insert_for(badge_name):
        if not badge_name:
            return None

        return BadgeStat.get_or_insert(
                key_name = "badgestat_%s" % badge_name,
                badge_name = badge_name,
                count_awarded = 0
                )

    @staticmethod
    def count_by_badge_name(badge_name):
        badge = BadgeStat.get_or_insert_for(badge_name)
        return badge.count_awarded

    def recalculate(self):
        self.count_awarded = UserBadge.count_by_badge_name(self.badge_name)
        self.dt_last_calculated = datetime.datetime.now()

class UserBadge(db.Model):
    user = db.UserProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    badge_name = db.StringProperty()
    target_context = db.ReferenceProperty()
    target_context_name = db.StringProperty()
    points_earned = db.IntegerProperty(default = 0)

    @staticmethod
    def get_for(user):
        query = UserBadge.all()
        query.filter('user =', user)
        query.order('badge_name')
        query.order('-date')
        return query.fetch(1000)

    @staticmethod
    def get_for_user_between_dts(user, dt_a, dt_b):
        query = UserBadge.all()
        query.filter('user =', user)
        query.filter('date >=', dt_a)
        query.filter('date <=', dt_b)
        query.order('date')
        return query

    @staticmethod
    def count_by_badge_name(name):
        query = UserBadge.all(keys_only=True)
        query.filter('badge_name = ', name)
        return query.count(1000000)

