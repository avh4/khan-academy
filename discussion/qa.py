import os

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from mapreduce import control
from mapreduce import operation as op

from django.utils import simplejson
from collections import defaultdict
import models
import models_discussion
import notification
from render import render_block_to_string
from util_discussion import is_honeypot_empty, is_current_user_moderator
import app
import util
import request_handler
import privileges

class ModeratorList(request_handler.RequestHandler):

    def get(self):

        # Must be an admin to change moderators
        if not users.is_current_user_admin():
            return

        mods = models.UserData.gql("WHERE moderator = :1", True)
        self.render_template('discussion/mod_list.html', {"mods" : mods})

    def post(self):

        # Must be an admin to change moderators
        if not users.is_current_user_admin():
            return

        user = users.User(self.request.get("user"))
        user_data = models.UserData.get_for(user)

        if user_data is not None:
            user_data.moderator = (self.request.get("mod") == "1")
            db.put(user_data)

        self.redirect("/discussion/moderatorlist")

class FlaggedFeedback(request_handler.RequestHandler):

    def get(self):

        if not is_current_user_moderator():
            self.redirect(users.create_login_url(self.request.uri))
            return

        # Show all non-deleted feedback flagged for moderator attention
        feedback_query = models_discussion.Feedback.all().filter("is_flagged = ", True).filter("deleted = ", False)

        feedback_count = feedback_query.count()
        feedbacks = feedback_query.fetch(25)
        self.render_template("discussion/flagged_feedback.html", {"feedbacks": feedbacks, "feedback_count": feedback_count})

def feedback_flag_update_map(feedback):
    feedback.recalculate_flagged()
    yield op.db.Put(feedback)

class StartNewFlagUpdateMapReduce(request_handler.RequestHandler):
    def get(self):
        mapreduce_id = control.start_map(
                name = "FeedbackFlagUpdate",
                handler_spec = "discussion.qa.feedback_flag_update_map",
                reader_spec = "mapreduce.input_readers.DatastoreInputReader",
                reader_parameters = {"entity_kind": "discussion.models_discussion.Feedback"},
                shard_count = 64,
                queue_name = "backfill-mapreduce-queue",
                )
        self.response.out.write("OK: " + str(mapreduce_id))

class ExpandQuestion(request_handler.RequestHandler):

    def post(self):
        notification.clear_question_answers_for_current_user(self.request.get("qa_expand_id"))

class PageQuestions(request_handler.RequestHandler):

    def get(self):

        page = 0
        try:
            page = int(self.request.get("page"))
        except:
            pass

        video_key = self.request.get("video_key")
        playlist_key = self.request.get("playlist_key")
        qa_expand_id = int(self.request.get("qa_expand_id")) if self.request.get("qa_expand_id") else -1
        video = db.get(video_key)
        playlist = db.get(playlist_key)

        if video:
            template_values = video_qa_context(video, playlist, page, qa_expand_id)
            path = os.path.join(os.path.dirname(__file__), 'video_qa.html')
            html = render_block_to_string(path, 'questions', template_values)
            json = simplejson.dumps({"html": html, "page": page}, ensure_ascii=False)
            self.response.out.write(json)

        return

class AddAnswer(request_handler.RequestHandler):

    def post(self):

        user = util.get_current_user()

        if not user:
            self.redirect(util.create_login_url(self.request.uri))
            return

        if not is_honeypot_empty(self.request):
            # Honeypot caught a spammer (in case this is ever public or spammers
            # have google accounts)!
            return

        answer_text = self.request.get("answer_text")
        video_key = self.request.get("video_key")
        question_key = self.request.get("question_key")

        video = db.get(video_key)
        question = db.get(question_key)

        if answer_text and video and question:

            answer = models_discussion.Feedback()
            answer.author = user
            answer.content = answer_text
            answer.targets = [video.key(), question.key()]
            answer.types = [models_discussion.FeedbackType.Answer]

            # We don't limit answer.content length, which means we're vulnerable to
            # RequestTooLargeErrors being thrown if somebody submits a POST over the GAE
            # limit of 1MB per entity.  This is *highly* unlikely for a legitimate piece of feedback,
            # and we're choosing to crash in this case until someone legitimately runs into this.
            # See Issue 841.
            db.put(answer)
            notification.new_answer_for_video_question(video, question, answer)

        self.redirect("/discussion/answers?question_key=%s" % question_key)

class Answers(request_handler.RequestHandler):

    def get(self):

        question_key = self.request.get("question_key")
        question = db.get(question_key)

        if question:
            answer_query = models_discussion.Feedback.gql("WHERE types = :1 AND targets = :2 AND deleted = :3 AND is_hidden_by_flags = :4 ORDER BY date", models_discussion.FeedbackType.Answer, question.key(), False, False)
            template_values = {
                "answers": answer_query,
                "is_mod": is_current_user_moderator()
            }
            path = os.path.join(os.path.dirname(__file__), 'question_answers.html')
            html = render_block_to_string(path, 'answers', template_values)
            json = simplejson.dumps({"html": html}, ensure_ascii=False)
            self.response.out.write(json)

        return

class AddQuestion(request_handler.RequestHandler):

    def post(self):

        user = util.get_current_user()

        if not user:
            self.redirect(util.create_login_url(self.request.uri))
            return

        if not is_honeypot_empty(self.request):
            # Honeypot caught a spammer (in case this is ever public or spammers
            # have google accounts)!
            return

        question_text = self.request.get("question_text")
        video_key = self.request.get("video_key")
        playlist_key = self.request.get("playlist_key")
        video = db.get(video_key)

        if question_text and video:
            if len(question_text) > 500:
                question_text = question_text[0:500] # max question length, also limited by client

            question = models_discussion.Feedback()
            question.author = user
            question.content = question_text
            question.targets = [video.key()]
            question.types = [models_discussion.FeedbackType.Question]
            db.put(question)

        self.redirect("/discussion/pagequestions?video_key=%s&playlist_key=%s&page=0" % (video_key, playlist_key))

class EditEntity(request_handler.RequestHandler):

    def post(self):

        user = util.get_current_user()
        if not user:
            return

        key = self.request.get("entity_key")
        playlist_key = self.request.get("playlist_key")
        text = self.request.get("question_text") or self.request.get("answer_text")

        if key and text:
            feedback = db.get(key)
            if feedback:
                if feedback.author == user or is_current_user_moderator():

                    feedback.content = text
                    db.put(feedback)

                    # Redirect to appropriate list of entities depending on type of 
                    # feedback entity being edited.
                    if feedback.is_type(models_discussion.FeedbackType.Question):

                        page = self.request.get("page")
                        video = feedback.first_target()
                        self.redirect("/discussion/pagequestions?video_key=%s&playlist_key=%s&page=%s&qa_expand_id=%s" % 
                                        (video.key(), playlist_key, page, feedback.key().id()))

                    elif feedback.is_type(models_discussion.FeedbackType.Answer):

                        question = feedback.parent()
                        self.redirect("/discussion/answers?question_key=%s" % question.key())

class VoteEntity(request_handler.RequestHandler):
    def post(self):
        # You have to be logged in to vote
        user = util.get_current_user()
        if not user:
            return

        key = self.request_string("entity_key", default="")
        flag = self.request_string("flag", default="")
        if key and models_discussion.FeedbackFlag.is_valid(flag):
            entity = db.get(key)
            if entity and entity.add_flag_by(flag, user):
                entity.put()

class FlagEntity(request_handler.RequestHandler):
    def post(self):
        # You have to at least be logged in to flag
        user = util.get_current_user()
        if not user:
            return

        key = self.request_string("entity_key", default="")
        flag = self.request_string("flag", default="")
        if key and models_discussion.FeedbackFlag.is_valid(flag):
            entity = db.get(key)
            if entity and entity.add_flag_by(flag, user):
                entity.put()

class ClearFlags(request_handler.RequestHandler):
    def post(self):
        if not is_current_user_moderator():
            return

        key = self.request.get("entity_key")
        if key:
            entity = db.get(key)
            if entity:
                entity.clear_flags()
                entity.put()

        self.redirect("/discussion/flaggedfeedback")

class ChangeEntityType(request_handler.RequestHandler):

    def post(self):

        # Must be a moderator to change types of anything
        if not is_current_user_moderator():
            return

        key = self.request.get("entity_key")
        target_type = self.request.get("target_type")
        if key and models_discussion.FeedbackType.is_valid(target_type):
            entity = db.get(key)
            if entity:
                entity.types = [target_type]
                db.put(entity)

class DeleteEntity(request_handler.RequestHandler):

    def post(self):

        user = util.get_current_user()
        if not user:
            return

        key = self.request.get("entity_key")
        if key:
            entity = db.get(key)
            if entity:
                # Must be a moderator or author of entity to delete
                if entity.author == user or is_current_user_moderator():
                    entity.deleted = True
                    db.put(entity)

        self.redirect("/discussion/flaggedfeedback")

def video_qa_context(video, playlist=None, page=0, qa_expand_id=None):

    limit_per_page = 5

    if qa_expand_id:
        # If we're showing an initially expanded question,
        # make sure we're on the correct page
        question = models_discussion.Feedback.get_by_id(qa_expand_id)
        if question:
            question_preceding_query = models_discussion.Feedback.gql("WHERE types = :1 AND targets = :2 AND deleted = :3 AND is_hidden_by_flags = :4 AND date > :5 ORDER BY date DESC", models_discussion.FeedbackType.Question, video.key(), False, False, question.date)
            count_preceding = question_preceding_query.count()
            page = 1 + (count_preceding / limit_per_page)

    if page <= 0:
        page = 1

    question_query = models_discussion.Feedback.gql("WHERE types = :1 AND targets = :2 AND deleted = :3 AND is_hidden_by_flags = :4 ORDER BY date DESC", models_discussion.FeedbackType.Question, video.key(), False, False)
    answer_query = models_discussion.Feedback.gql("WHERE types = :1 AND targets = :2 AND deleted = :3 AND is_hidden_by_flags = :4 ORDER BY date", models_discussion.FeedbackType.Answer, video.key(), False, False)

    count_total = question_query.count()
    questions = question_query.fetch(limit_per_page, (page - 1) * limit_per_page)

    dict_questions = {}
    # Store each question in this page in a dict for answer population
    for question in questions:
        dict_questions[question.key()] = question

    # Just grab all answers for this video and cache in page's questions
    for answer in answer_query:
        # Grab the key only for each answer, don't run a full gql query on the ReferenceProperty
        question_key = answer.parent_key()
        if (dict_questions.has_key(question_key)):
            question = dict_questions[question_key]
            question.children_cache.append(answer)

    count_page = len(questions)
    pages_total = max(1, ((count_total - 1) / limit_per_page) + 1)
    return {
            "user": util.get_current_user(),
            "is_mod": is_current_user_moderator(),
            "video": video,
            "playlist": playlist,
            "questions": questions,
            "count_total": count_total,
            "pages": range(1, pages_total + 1),
            "pages_total": pages_total,
            "prev_page_1_based": page - 1,
            "current_page_1_based": page,
            "next_page_1_based": page + 1,
            "show_page_controls": pages_total > 1,
            "qa_expand_id": qa_expand_id,
            "issue_labels": ('Component-Videos,Video-%s' % video.youtube_id),
            "login_url": util.create_login_url("/video?v=%s" % video.youtube_id)
           }

def add_template_values(dict, request):
    dict["comments_page"] = int(request.get("comments_page")) if request.get("comments_page") else 0
    dict["qa_page"] = int(request.get("qa_page")) if request.get("qa_page") else 0
    dict["qa_expand_id"] = int(request.get("qa_expand_id")) if request.get("qa_expand_id") else -1

    return dict
