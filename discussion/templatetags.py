# import the webapp module
import re
from google.appengine.ext import webapp
from django import template

import models_discussion
from comments import video_comments_context
from qa import video_qa_context
from util import is_current_user_moderator

import app

register = webapp.template.create_template_register()

@register.inclusion_tag("discussion/video_comments.html")
def video_comments(video, page=0):
    return video_comments_context(video, page)

@register.inclusion_tag("discussion/video_qa.html")
def video_qa(video, page=0, qa_expand_id=None):
    return video_qa_context(video, page, qa_expand_id)

@register.inclusion_tag(("discussion/signature.html", "signature.html"))
def signature(target=None, verb=None):
    return {
                "target": target, 
                "verb": verb, 
                "is_mod": is_current_user_moderator(),
                "is_author": target and target.author == app.get_current_user()
            }

@register.inclusion_tag(("discussion/mod_tools.html", "mod_tools.html"))
def mod_tools(target):
    return {
                "target": target,
                "type_question": models_discussion.FeedbackType.Question,
                "type_comment": models_discussion.FeedbackType.Comment,
                "is_question": target.is_type(models_discussion.FeedbackType.Question),
                "is_comment": target.is_type(models_discussion.FeedbackType.Comment)
            }

@register.inclusion_tag(("discussion/author_tools.html", "author_tools.html"))
def author_tools(target):
    return {
                "target": target,
                "editable": not target.is_type(models_discussion.FeedbackType.Comment)
            }

@register.inclusion_tag(("discussion/question_answers.html", "question_answers.html"))
def question_answers(answers):
    return { "answers": answers }

@register.inclusion_tag(("discussion/question_answers.html", "question_answers.html"))
def standalone_answers(video, dict_answers):
    return { "answers": dict_answers[video.key()], "video": video, "standalone": True }

@register.inclusion_tag(("discussion/username_and_notification.html", "username_and_notification.html"))
def username_and_notification(username):
    count = models_discussion.FeedbackNotification.gql("WHERE user = :1", app.get_current_user()).count()
    return { "username": username, "count": count }

@register.inclusion_tag(("discussion/feedback_controls.html","feedback_controls.html"))
def feedback_controls_question(button_label, target=None):
    return {
                "feedback_type": models_discussion.FeedbackType.Question,
                "button_label": button_label,
                "show_chars_remaining": True,
                "target": target,
                "hidden": True
            }

@register.inclusion_tag(("discussion/feedback_controls.html","feedback_controls.html"))
def feedback_controls_answer(button_label, target=None):
    return {
                "feedback_type": models_discussion.FeedbackType.Answer,
                "button_label": button_label,
                "show_chars_remaining": False,
                "target": target,
                "hidden": True
            }

@register.inclusion_tag(("discussion/feedback_controls.html","feedback_controls.html"))
def feedback_controls_comment(button_label, target=None):
    return {
                "feedback_type": models_discussion.FeedbackType.Comment,
                "button_label": button_label,
                "show_chars_remaining": True,
                "target": target,
                "hidden": False
            }

@register.inclusion_tag(("discussion/honeypots.html", "honeypots.html"))
def honeypots():
    # Honeypots are used to attact spam bots
    return {}
