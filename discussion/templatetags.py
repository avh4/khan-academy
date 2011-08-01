import os
import re
from google.appengine.ext import webapp
from django import template

import models
import models_discussion
from comments import video_comments_context
from qa import video_qa_context
from util_discussion import is_current_user_moderator
import voting
import app
import util

import template_cached
register = template_cached.create_template_register()

@register.inclusion_tag("discussion/video_comments.html")
def video_comments(video, playlist, page=0):
    user_data = models.UserData.current()
    return {
            "video": video,
            "playlist": playlist,
            "page": 0,
            "logged_in": user_data and not user_data.is_phantom,
            "user_data": user_data,
            "login_url": util.create_login_url("/video?v=%s" % video.youtube_id),
            }

@register.inclusion_tag("discussion/video_qa.html")
def video_qa(user_data, video, playlist, page=0, qa_expand_id=None, sort_override=-1):

    sort_order = voting.VotingSortOrder.HighestPointsFirst
    if user_data:
        sort_order = user_data.question_sort_order
    if sort_override >= 0:
        sort_order = sort_override

    return {
            "user_data": user_data,
            "video": video,
            "playlist": playlist,
            "page": page,
            "qa_expand_id": qa_expand_id,
            "sort_order": sort_order,
            "logged_in": user_data and not user_data.is_phantom,
            "login_url": util.create_login_url("/video?v=%s" % video.youtube_id),
            "issue_labels": ('Component-Videos,Video-%s' % video.youtube_id),
            }

@register.inclusion_tag("discussion/signature.html")
def signature(target=None, verb=None):
    return {
                "target": target,
                "verb": verb,
                "is_mod": is_current_user_moderator(),
                "is_author": target and target.authored_by(models.UserData.current()),
                "is_comment": target and target.is_type(models_discussion.FeedbackType.Comment),
            }

@register.inclusion_tag("discussion/mod_tools.html")
def mod_tools(target):
    return {
                "target": target,
                "type_question": models_discussion.FeedbackType.Question,
                "type_comment": models_discussion.FeedbackType.Comment,
                "is_question": target.is_type(models_discussion.FeedbackType.Question),
                "is_comment": target.is_type(models_discussion.FeedbackType.Comment)
            }

@register.inclusion_tag("discussion/flag_tools.html")
def flag_tools(target):
    return {"target": target}

@register.inclusion_tag("discussion/vote_tools.html")
def vote_tools(target):
    return { "target": target, "is_comment": target.is_type(models_discussion.FeedbackType.Comment) }

@register.inclusion_tag("discussion/vote_sum.html")
def vote_sum(target):
    sum_original = target.sum_votes_incremented()
    if target.up_voted:
        sum_original -= 1
    elif target.down_voted:
        sum_original += 1

    return {
            "target": target,
            "sum_original": sum_original,
            "is_comment": target.is_type(models_discussion.FeedbackType.Comment),
            }

@register.inclusion_tag("discussion/author_tools.html")
def author_tools(target):
    return {
                "target": target,
                "editable": not target.is_type(models_discussion.FeedbackType.Comment)
            }

@register.inclusion_tag("discussion/question_answers.html")
def question_answers(answers):
    return { "answers": answers }

@register.inclusion_tag("discussion/question_answers.html")
def standalone_answers(video, playlist, dict_answers):
    return { "answers": dict_answers[video.key()], "video": video, "playlist": playlist, "standalone": True }

@register.inclusion_tag("discussion/username_and_notification.html")
def username_and_notification(username, user_data):
    count = user_data.feedback_notification_count() if user_data else 0
    return { "username": username, "count": count }

@register.inclusion_tag("discussion/feedback_controls.html")
def feedback_controls_question(button_label, target=None):
    return {
                "feedback_type": models_discussion.FeedbackType.Question,
                "button_label": button_label,
                "show_chars_remaining": True,
                "target": target,
                "hidden": True
            }

@register.inclusion_tag("discussion/feedback_controls.html")
def feedback_controls_answer(button_label, target=None):
    return {
                "feedback_type": models_discussion.FeedbackType.Answer,
                "button_label": button_label,
                "show_chars_remaining": False,
                "target": target,
                "hidden": True
            }

@register.inclusion_tag("discussion/feedback_controls.html")
def feedback_controls_comment(button_label, target=None):
    return {
                "feedback_type": models_discussion.FeedbackType.Comment,
                "button_label": button_label,
                "show_chars_remaining": True,
                "target": target,
                "hidden": False
            }

@register.inclusion_tag("discussion/honeypots.html")
def honeypots():
    # Honeypots are used to attact spam bots
    return {}
