#!/usr/bin/python
# -*- coding: utf-8 -*-
from google.appengine.ext import db

class Comment(db.Model):

    author = db.UserProperty()
    content = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)
    deleted = db.BooleanProperty(default=False)
    target = db.ReferenceProperty()

class DiscussQuestion(db.Model):

    author = db.UserProperty()
    content = db.TextProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    deleted = db.BooleanProperty(default=False)
    target = db.ReferenceProperty()

    def __init__(self, *args, **kwargs):
        db.Model.__init__(self, *args, **kwargs)
        self.answers = [] # For caching each question's answers during render

class DiscussAnswer(db.Model):

    author = db.UserProperty()
    content = db.TextProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    deleted = db.BooleanProperty(default=False)
    question = db.ReferenceProperty(DiscussQuestion, 
                    collection_name="question_reference_set") # Avoid any DuplicatePropertyError with the generic target ReferenceProperty
    target = db.ReferenceProperty()
