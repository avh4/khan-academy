import os

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from app import App
from app import get_nickname_for
import app
import models
import models_discussion

class VideoFeedbackNotificationList(app.RequestHandler):

    def get(self):

        user = app.get_current_user()

        if not user:
            self.redirect(app.create_login_url(self.request.uri))
            return

        answers = feedback_answers_for_user(user)

        dict_videos = {}
        dict_answers = {}

        for answer in answers:

            video = answer.first_target()

            if video == None or type(video).__name__ != "Video":
                continue

            video_key = video.key()
            dict_videos[video_key] = video
            
            if dict_answers.has_key(video_key):
                dict_answers[video_key].append(answer)
            else:
                dict_answers[video_key] = [answer]

        videos = sorted(dict_videos.values(), key=lambda video: video.playlists[0] + video.title)
        user_data = models.UserData.get_for_current_user()

        context = {
                    "App": App,
                    "points": user_data.points,
                    "username": get_nickname_for(user),
                    "email": user.email(),
                    "login_url": app.create_login_url(self.request.uri),
                    "logout_url": users.create_logout_url(self.request.uri),
                    "videos": videos,
                    "dict_answers": dict_answers
                  }

        path = os.path.join(os.path.dirname(__file__), 'video_feedback_notification_list.html')
        self.response.out.write(template.render(path, context))

class VideoFeedbackNotificationFeed(app.RequestHandler):

    def get(self):

        user = None
        try:
            user = users.User(self.request.get("email"))
        except:
            user = None

        max_entries = 100
        answers = feedback_answers_for_user(user)
        answers = sorted(answers, key=lambda answer: answer.date)

        context = {
                    "answers": answers,
                    "count": len(answers)
                  }

        self.response.headers['Content-Type'] = 'text/xml'
        path = os.path.join(os.path.dirname(__file__), 'video_feedback_notification_feed.xml')
        self.response.out.write(template.render(path, context))

def feedback_answers_for_user(user):
    notifications = models_discussion.FeedbackNotification.gql("WHERE user = :1", user)

    feedbacks = []

    for notification in notifications:

        feedback = notification.feedback

        if feedback == None or feedback.deleted or not feedback.is_type(models_discussion.FeedbackType.Answer):
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

    db.put(notification)

def clear_question_answers_for_current_user(s_question_id):

    user = app.get_current_user()
    if not user:
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
        notifications = models_discussion.FeedbackNotification.gql("WHERE user = :1 AND feedback = :2", user, key)
        if notifications.count():
            db.delete(notifications)

