#!/usr/bin/python
# -*- coding: utf-8 -*-
from google.appengine.ext import db

from util import get_nickname_for

class FeedbackType:
    Question="question"
    Answer="answer"
    Comment="comment"

    @staticmethod    
    def is_valid(type):
        return (type == FeedbackType.Question or 
                type == FeedbackType.Answer or 
                type == FeedbackType.Comment)

class Feedback(db.Model):
    author = db.UserProperty()
    content = db.TextProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    deleted = db.BooleanProperty(default=False)
    targets = db.ListProperty(db.Key)
    types = db.StringListProperty()

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

class FeedbackNotification(db.Model):
    feedback = db.ReferenceProperty(Feedback)
    user = db.UserProperty()
