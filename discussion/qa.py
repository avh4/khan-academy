import os

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from django.utils import simplejson

import models
from render import render_block_to_string
from util import is_honeypot_empty

class PageQuestions(webapp.RequestHandler):

    def get(self):

        page = 0
        try:
            page = int(self.request.get("page"))
        except:
            pass

        video_key = self.request.get("video_key")
        video = db.get(video_key)

        if video:
            questions_hidden = (self.request.get("questions_hidden") == "1")
            template_values = video_qa_context(video, page, None, questions_hidden)
            path = os.path.join(os.path.dirname(__file__), 'video_qa.html')
            html = render_block_to_string(path, 'questions', template_values)
            json = simplejson.dumps({"html": html, "page": page}, ensure_ascii=False)
            self.response.out.write(json)

        return

class AddAnswer(webapp.RequestHandler):

    def post(self):

        user = users.get_current_user()

        if not user:
            self.redirect(users.create_login_url(self.request.uri))
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
            if len(answer_text) > 500:
                answer_text = answer_text[0:500] # max answer length, also limited by client

            answer = models.DiscussAnswer()
            answer.author = user
            answer.content = answer_text
            answer.targets = [video.key(), question.key()]
            db.put(answer)

        self.redirect("/discussion/answers?question_key=%s" % question_key)

class Answers(webapp.RequestHandler):

    def get(self):

        question_key = self.request.get("question_key")
        question = db.get(question_key)

        if question:
            answer_query = models.DiscussAnswer.gql("WHERE targets = :1 AND deleted = :2 ORDER BY date", question.key(), False)
            template_values = {
                "answers": answer_query,
                "is_admin": users.is_current_user_admin()
            }
            path = os.path.join(os.path.dirname(__file__), 'question_answers.html')
            html = render_block_to_string(path, 'answers', template_values)
            json = simplejson.dumps({"html": html}, ensure_ascii=False)
            self.response.out.write(json)

        return

class AddQuestion(webapp.RequestHandler):

    def post(self):

        user = users.get_current_user()

        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return

        if not is_honeypot_empty(self.request):
            # Honeypot caught a spammer (in case this is ever public or spammers
            # have google accounts)!
            return

        question_text = self.request.get("question_text")
        questions_hidden = self.request.get("questions_hidden")
        video_key = self.request.get("video_key")
        video = db.get(video_key)

        if question_text and video:
            if len(question_text) > 500:
                question_text = question_text[0:500] # max question length, also limited by client

            question = models.DiscussQuestion()
            question.author = user
            question.content = question_text
            question.targets = [video.key()]
            db.put(question)

        self.redirect("/discussion/pagequestions?video_key=%s&page=0&questions_hidden=%s" % (video_key, questions_hidden))

class DeleteEntity(webapp.RequestHandler):

    def post(self):

        # Must be an admin to delete anything
        if not users.is_current_user_admin():
            return

        key = self.request.get("entity_key")
        if key:
            entity = db.get(key)
            if entity:
                entity.deleted = True
                db.put(entity)

def video_qa_context(video, page=0, qa_expand_id=None, questions_hidden=True):

    limit_per_page = 10

    if qa_expand_id:
        # If we're showing an initially expanded question,
        # make sure we're on the correct page
        question = models.DiscussQuestion.get_by_id(qa_expand_id)
        if question:
            question_preceding_query = models.DiscussQuestion.gql("WHERE targets = :1 AND deleted = :2 AND date > :3 ORDER BY date DESC", video.key(), False, question.date)
            count_preceding = question_preceding_query.count()
            page = 1 + (count_preceding / limit_per_page)        

    if page > 0:
        questions_hidden = False # Never hide questions if specifying specific page
    else:
        page = 1

    limit_initially_visible = 3 if questions_hidden else limit_per_page

    question_query = models.DiscussQuestion.gql("WHERE targets = :1 AND deleted = :2 ORDER BY date DESC", video.key(), False)
    answer_query = models.DiscussAnswer.gql("WHERE targets = :1 AND deleted = :2 ORDER BY date", video.key(), False)

    count_total = question_query.count()
    questions = question_query.fetch(limit_per_page, (page - 1) * limit_per_page)

    dict_questions = {}
    # Store each question in this page in a dict for answer population
    for question in questions:
        dict_questions[question.key()] = question

    # Just grab all answers for this video and cache in page's questions
    for answer in answer_query:
        # Grab the key only for each answer, don't run a full gql query on the ReferenceProperty
        question_key = answer.parent()
        if (dict_questions.has_key(question_key)):
            question = dict_questions[question_key]
            question.answers_cache.append(answer)

    count_page = len(questions)
    pages_total = max(1, ((count_total - 1) / limit_per_page) + 1)
    return {
            "user": users.get_current_user(),
            "is_admin": users.is_current_user_admin(),
            "video": video,
            "questions": questions,
            "count_total": count_total,
            "questions_hidden": count_page > limit_initially_visible,
            "limit_initially_visible": limit_initially_visible,
            "pages": range(1, pages_total + 1),
            "pages_total": pages_total,
            "prev_page_1_based": page - 1,
            "current_page_1_based": page,
            "next_page_1_based": page + 1,
            "show_page_controls": pages_total > 1,
            "qa_expand_id": qa_expand_id,
            "issue_labels": ('Component-Videos,Video-%s' % video.youtube_id),
            "login_url": users.create_login_url("/video?v=%s" % video.youtube_id)
           }

def add_template_values(dict, request):
    dict["comments_page"] = int(request.get("comments_page")) if request.get("comments_page") else 0
    dict["qa_page"] = int(request.get("qa_page")) if request.get("qa_page") else 0
    dict["qa_expand_id"] = int(request.get("qa_expand_id")) if request.get("qa_expand_id") else -1
    return dict
