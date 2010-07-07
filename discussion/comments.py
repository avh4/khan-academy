import os

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from django.utils import simplejson

import models
from render import render_block_to_string
from util import is_honeypot_empty

class PageComments(webapp.RequestHandler):

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

class AddComment(webapp.RequestHandler):

    def post(self):

        user = users.get_current_user()

        if not user:
            self.redirect(users.create_login_url(self.request.uri))
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

            comment = models.Comment()
            comment.author = user
            comment.content = comment_text
            comment.targets = [video.key()]
            db.put(comment)

        self.redirect("/discussion/pagecomments?video_key={0}&page=0&comments_hidden={1}".format(video_key, comments_hidden))

def video_comments_context(video, page=0, comments_hidden=True):

    if page > 0:
        comments_hidden = False # Never hide questions if specifying specific page
    else:
        page = 1

    limit_per_page = 10
    limit_initially_visible = 3 if comments_hidden else limit_per_page

    comments_query = models.Comment.gql("WHERE targets = :1 and deleted = :2 ORDER BY date DESC", video.key(), False)
    count_total = comments_query.count()
    comments = comments_query.fetch(limit_per_page, (page - 1) * limit_per_page)

    count_page = len(comments)
    pages_total = max(1, ((count_total - 1) / limit_per_page) + 1)
    return {
            "user": users.get_current_user(),
            "is_admin": users.is_current_user_admin(),
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
            "login_url": users.create_login_url("/video?v={0}".format(video.youtube_id))
           }
