import datetime

from google.appengine.ext import db

from app import App
import request_handler
import classtime
import util

import logging

class ViewProfile(request_handler.RequestHandler):

    def get(self):
        user = util.get_current_user()
        if user:
            dt_end_utc = datetime.datetime.now()
            dt_start_utc = dt_end_utc - datetime.timedelta(days = 10)

            classtime_analyzer = classtime.ClassTimeAnalyzer()
            classtime_table = classtime_analyzer.get_classtime_table([user.email()], dt_start_utc, dt_end_utc)

            template_values = {
                'classtime_table': classtime_table,
            }
            self.render_template('viewprofile.html', template_values)
        else:
            self.redirect(util.create_login_url(self.request.uri))

