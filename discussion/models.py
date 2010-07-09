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

    def parent(self):
        if self.targets:
            return self.targets[-1]
        return None

    def __init__(self, *args, **kwargs):
        db.Model.__init__(self, *args, **kwargs)
        self.children_cache = [] # For caching each question's answers during render
