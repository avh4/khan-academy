#!/usr/bin/python
# -*- coding: utf-8 -*-
from google.appengine.ext import db

class FeedbackType:
    Question="question"
    Answer="answer"
    Comment="comment"

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

    def first_target(self):
        if self.targets:
            return db.get(self.targets[0])
        return None
