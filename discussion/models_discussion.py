#!/usr/bin/python
# -*- coding: utf-8 -*-
from google.appengine.ext import db
from google.appengine.api import memcache

from app import App
from nicknames import get_nickname_for
import request_cache

class FeedbackType:
    Question="question"
    Answer="answer"
    Comment="comment"

    @staticmethod
    def is_valid(type):
        return (type == FeedbackType.Question or 
                type == FeedbackType.Answer or 
                type == FeedbackType.Comment)

class FeedbackFlag:

    # 2 or more flags immediately hides feedback
    HIDE_LIMIT = 2

    Inappropriate="inappropriate"
    LowQuality="lowquality"
    DoesNotBelong="doesnotbelong"
    Spam="spam"

    @staticmethod
    def is_valid(flag):
        return (flag == FeedbackFlag.Inappropriate or 
                flag == FeedbackFlag.LowQuality or 
                flag == FeedbackFlag.DoesNotBelong or 
                flag == FeedbackFlag.Spam)

class Feedback(db.Model):
    author = db.UserProperty()
    content = db.TextProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    deleted = db.BooleanProperty(default=False)
    targets = db.ListProperty(db.Key)
    types = db.StringListProperty()
    is_flagged = db.BooleanProperty(default=False)
    is_hidden_by_flags = db.BooleanProperty(default=False)
    flags = db.StringListProperty(default=None)
    flagged_by = db.StringListProperty(default=None)
    sum_votes = db.IntegerProperty(default=0)

    @staticmethod
    def memcache_key_for_video(video):
        return "video_feedback_%s" % video.key()

    def __init__(self, *args, **kwargs):
        db.Model.__init__(self, *args, **kwargs)
        self.children_cache = [] # For caching each question's answers during render

    def put(self):
        memcache.delete(Feedback.memcache_key_for_video(self.first_target()), namespace=App.version)
        db.Model.put(self)

    def is_type(self, type):
        return type in self.types

    def parent_key(self):
        if self.targets:
            return self.targets[-1]
        return None

    def parent(self):
        return db.get(self.parent_key())

    def children_keys(self):
        keys = db.Query(Feedback, keys_only=True)
        keys.filter("targets = ", self.key())
        return keys

    def first_target_key(self):
        if self.targets:
            return self.targets[0]
        return None

    def first_target(self):
        target_key = self.first_target_key()
        if target_key:
            return db.get(target_key)
        return None

    def author_nickname(self):
        return get_nickname_for(self.author)

    def add_vote_by(self, vote_type, user):
        FeedbackVote.add_vote(self, vote_type, user)
        self.sum_votes = FeedbackVote.count_votes(self)
        return True

    def add_flag_by(self, flag_type, user):
        if user.email() in self.flagged_by:
            return False

        self.flags.append(flag_type)
        self.flagged_by.append(user.email())
        self.recalculate_flagged()
        return True

    def clear_flags(self):
        self.flags = []
        self.flagged_by = []
        self.recalculate_flagged()

    def recalculate_flagged(self):
        self.is_flagged = len(self.flags or []) > 0
        self.is_hidden_by_flags = len(self.flags or []) >= FeedbackFlag.HIDE_LIMIT

class FeedbackNotification(db.Model):
    feedback = db.ReferenceProperty(Feedback)
    user = db.UserProperty()

class FeedbackVote(db.Model):
    ABSTAIN = 0
    UP = 1
    DOWN = 2

    # Feedback reference stored in parent property
    video = db.ReferenceProperty()
    user = db.UserProperty()
    vote_type = db.IntegerProperty(default=0)

    @staticmethod
    def add_vote(feedback, vote_type, user):
        if not feedback:
            return

        vote = FeedbackVote.get_or_insert(
                key_name = "vote_by_%s" % user.email(),
                parent = feedback,
                video = feedback.first_target_key(),
                user = user,
                vote_type = vote_type)

        if vote and vote.vote_type != vote_type:
            # If vote already existed and user has changed vote, update
            vote.vote_type = vote_type
            vote.put()

    @staticmethod
    @request_cache.cache_with_key_fxn(lambda user, video: "voting_dict_for_%s" % video.key())
    def get_dict_for_user_and_video(user, video):
        query = FeedbackVote.all()
        query.filter("user =", user)
        query.filter("video =", video)
        votes = query.fetch(1000)

        dict = {}
        for vote in votes:
            dict[vote.parent_key()] = vote

        return dict

    @staticmethod
    def count_votes(feedback):
        if not feedback:
            return 0

        query = FeedbackVote.all()
        query.ancestor(feedback)
        votes = query.fetch(100000)

        count_up = len(filter(lambda vote: vote.is_up(), votes))
        count_down = len(filter(lambda vote: vote.is_down(), votes))

        return count_up - count_down

    def is_up(self):
        return self.vote_type == FeedbackVote.UP

    def is_down(self):
        return self.vote_type == FeedbackVote.DOWN
