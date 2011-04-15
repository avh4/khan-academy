#!/usr/bin/python
# -*- coding: utf-8 -*-
from google.appengine.ext import db

from nicknames import get_nickname_for

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

    def __init__(self, *args, **kwargs):
        db.Model.__init__(self, *args, **kwargs)
        self.children_cache = [] # For caching each question's answers during render

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

    def first_target(self):
        if self.targets:
            return db.get(self.targets[0])
        return None

    def author_nickname(self):
        return get_nickname_for(self.author)

    def add_vote_by(self, vote_type, user):
        FeedbackVote.add_vote(self, vote_type, user)
        self.sum_votes = FeedbackVote.count_votes(self)

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

    user = db.UserProperty()
    vote_type = db.IntegerProperty(default=0)

    @staticmethod
    def add_vote(feedback, vote_type, user):
        if not feedback:
            return

        vote = FeedbackVote.get_or_insert(
                key_name = "vote_by_%s" % user.email(),
                parent = feedback,
                user = user,
                vote_type = vote_type)

        if vote and vote.vote_type != vote_type:
            # If vote already existed and user has changed vote, update
            vote.vote_type = vote_type
            vote.put()

    @staticmethod
    def count_votes(feedback):
        if not feedback:
            return 0

        query_up = FeedbackVote.all()
        query_up.ancestor(feedback)
        query_up.filter("vote_type = ", FeedbackVote.UP)

        query_down = FeedbackVote.all()
        query_down.ancestor(feedback)
        query_down.filter("vote_type = ", FeedbackVote.DOWN)

        return query_up.count() - query_down.count()

