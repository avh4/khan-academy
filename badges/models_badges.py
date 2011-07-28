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

class CustomBadgeType(db.Model):
    description = db.StringProperty()
    full_description = db.TextProperty()
    points = db.IntegerProperty(default = 0)
    category = db.IntegerProperty(default = 0)
    icon_src = db.StringProperty(default = "")

    @staticmethod
    def insert(name, description, full_description, points, badge_category, icon_src = ""):

        if not name or not description or not full_description or points < 0 or badge_category < 0:
            return None

        if icon_src and not icon_src.startswith("/"):
            return None

        custom_badge_type = CustomBadgeType.get_by_key_name(key_names = name)
        if not custom_badge_type:
            return CustomBadgeType.get_or_insert(
                    key_name = name,
                    description = description,
                    full_description = full_description,
                    points = points,
                    category = badge_category,
                    icon_src = icon_src
                    )

        return None

class UserBadge(db.Model):
    user = db.UserProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    badge_name = db.StringProperty()
    target_context = db.ReferenceProperty()
    target_context_name = db.StringProperty()
    points_earned = db.IntegerProperty(default = 0)

    _serialize_blacklist = ["badge"]

    @staticmethod
    def get_for(user_data):
        query = UserBadge.all()
        query.filter('user =', user_data.user)
        query.order('badge_name')
        query.order('-date')
        return query.fetch(1000)

    @staticmethod
    def get_for_user_data_between_dts(user_data, dt_a, dt_b):
        query = UserBadge.all()
        query.filter('user =', user_data.user)
        query.filter('date >=', dt_a)
        query.filter('date <=', dt_b)
        query.order('date')
        return query

    @staticmethod
    def count_by_badge_name(name):
        query = UserBadge.all(keys_only=True)
        query.filter('badge_name = ', name)
        return query.count(1000000)

