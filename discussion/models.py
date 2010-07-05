#!/usr/bin/python
# -*- coding: utf-8 -*-
from google.appengine.ext import db

class Feedback(db.Model):
    author = db.UserProperty()
    content = db.TextProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    deleted = db.BooleanProperty(default=False)
    targets = db.ListProperty(db.Key)

    def parent(self):
        if self.targets:
            return self.targets[-1]
        return None

class DiscussQuestion(Feedback):

    def __init__(self, *args, **kwargs):
        Feedback.__init__(self, *args, **kwargs)
        self.answers_cache = [] # For caching each question's answers during render

class DiscussAnswer(Feedback):
    pass

class Comment(Feedback):
    pass
