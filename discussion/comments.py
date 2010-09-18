import os

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from django.utils import simplejson

import models_discussion
from render import render_block_to_string
from util import is_honeypot_empty, is_current_user_moderator
import app

class PageComments(app.RequestHandler):

    def get(self):

        page = 0
        try:
            page = int(self.request.get("page"))
        except:
            pass

        video_key = self.request.get("video_key")
        video = db.get(video_key)

        if video:
            comments_hidden = (self.request.get("comments_hidden") == "1")
            template_values = video_comments_context(video, page, comments_hidden)
            path = os.path.join(os.path.dirname(__file__), 'video_comments.html')

            html = render_block_to_string(path, 'comments', template_values)
            json = simplejson.dumps({"html": html, "page": page}, ensure_ascii=False)
            self.response.out.write(json)

class AddComment(app.RequestHandler):

    def post(self):

        user = app.get_current_user()

        if not user:
            self.redirect(app.create_login_url(self.request.uri))
            return

        if not is_honeypot_empty(self.request):
            # Honeypot caught a spammer (in case this is ever public or spammers
            # have google accounts)!
            return

        comment_text = self.request.get("comment_text")
        comments_hidden = self.request.get("comments_hidden")
        video_key = self.request.get("video_key")
        video = db.get(video_key)

        if comment_text and video:
            if len(comment_text) > 300:
                comment_text = comment_text[0:300] # max comment length, also limited by client

            comment = models_discussion.Feedback()
            comment.author = user
            comment.content = comment_text
            comment.targets = [video.key()]
            comment.types = [models_discussion.FeedbackType.Comment]
            db.put(comment)

        self.redirect("/discussion/pagecomments?video_key=%s&page=0&comments_hidden=%s" % (video_key, comments_hidden))

def video_comments_context(video, page=0, comments_hidden=True):

    if page > 0:
        comments_hidden = False # Never hide questions if specifying specific page
    else:
        page = 1

    limit_per_page = 10
    limit_initially_visible = 3 if comments_hidden else limit_per_page

    comments_query = models_discussion.Feedback.gql("WHERE types = :1 AND targets = :2 AND deleted = :3 ORDER BY date DESC", models_discussion.FeedbackType.Comment, video.key(), False)
    count_total = comments_query.count()
    comments = comments_query.fetch(limit_per_page, (page - 1) * limit_per_page)

    count_page = len(comments)
    pages_total = max(1, ((count_total - 1) / limit_per_page) + 1)
    return {
            "user": app.get_current_user(),
            "is_mod": is_current_user_moderator(),
            "video": video,
            "comments": comments,
            "count_total": count_total,
            "comments_hidden": count_page > limit_initially_visible,
            "limit_initially_visible": limit_initially_visible,
            "pages": range(1, pages_total + 1),
            "pages_total": pages_total,
            "prev_page_1_based": page - 1,
            "current_page_1_based": page,
            "next_page_1_based": page + 1,
            "show_page_controls": pages_total > 1,
            "login_url": app.create_login_url("/video?v=%s" % video.youtube_id)
           }
