import os

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from app import App
from util import get_nickname_for
import app
import util
import util_discussion
import request_handler
import models
import models_discussion
import voting

class VideoFeedbackNotificationList(request_handler.RequestHandler):

    def get(self):

        user_data = models.UserData.current()

        if not user_data:
            self.redirect(util.create_login_url(self.request.uri))
            return

        answers = feedback_answers_for_user_data(user_data)

        dict_videos = {}
        dict_answers = {}

        for answer in answers:

            video = answer.first_target()

            dict_votes = models_discussion.FeedbackVote.get_dict_for_user_data_and_video(user_data, video)
            voting.add_vote_expando_properties(answer, dict_votes)

            if video == None or type(video).__name__ != "Video":
                continue

            video_key = video.key()
            dict_videos[video_key] = video
            
            if dict_answers.has_key(video_key):
                dict_answers[video_key].append(answer)
            else:
                dict_answers[video_key] = [answer]

        videos = sorted(dict_videos.values(), key=lambda video: video.playlists[0] + video.title)

        context = {
                    "email": user_data.display_email,
                    "videos": videos,
                    "dict_answers": dict_answers
                  }

        self.render_template('discussion/video_feedback_notification_list.html', context)

class VideoFeedbackNotificationFeed(request_handler.RequestHandler):

    def get(self):

        user_data = self.request_user_data("email")

        max_entries = 100
        answers = feedback_answers_for_user_data(user_data)
        answers = sorted(answers, key=lambda answer: answer.date)

        context = {
                    "answers": answers,
                    "count": len(answers)
                  }

        self.response.headers['Content-Type'] = 'text/xml'
        self.render_template('discussion/video_feedback_notification_feed.xml', context)

def feedback_answers_for_user_data(user_data):
    notifications = models_discussion.FeedbackNotification.gql("WHERE user = :1", user_data.user)

    feedbacks = []

    for notification in notifications:

        feedback = notification.feedback

        if feedback == None or feedback.deleted or feedback.is_hidden_by_flags or not feedback.is_type(models_discussion.FeedbackType.Answer):
            # If we ever run into notification for a deleted or non-FeedbackType.Answer piece of feedback,
            # go ahead and clear the notification so we keep the DB clean.
            if feedback:
                db.delete(notification)
            continue

        feedbacks.append(feedback)

    return feedbacks

# Send a notification to the author of this question, letting
# them know that a new answer is available.
def new_answer_for_video_question(video, question, answer):

    if not question or not question.author:
        return

    # Don't notify if user answering own question
    if question.author == answer.author:
        return

    notification = models_discussion.FeedbackNotification()
    notification.user = question.author
    notification.feedback = answer

    user_data = models.UserData.get_or_insert_for(notification.user)
    user_data.count_feedback_notification = -1

    db.put([notification, user_data])

def clear_question_answers_for_current_user(s_question_id):

    user_data = models.UserData.current()

    if not user_data:
        return

    question_id = -1
    try:
        question_id = int(s_question_id)
    except:
        return

    if question_id < 0:
        return

    question = models_discussion.Feedback.get_by_id(question_id)
    if not question:
        return;

    feedback_keys = question.children_keys()
    for key in feedback_keys:
        notifications = models_discussion.FeedbackNotification.gql("WHERE user = :1 AND feedback = :2", user_data.user, key)
        if notifications.count():
            db.delete(notifications)

    user_data.count_feedback_notification = -1
    user_data.put()


