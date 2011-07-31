import logging

from google.appengine.api import users

import request_handler
from dashboard.models import DailyStatistic

class Dashboard(request_handler.RequestHandler):

    def get(self):
        if not users.is_current_user_admin():
            self.redirect(users.create_login_url(self.request.uri))
            return

        # Grab last ~4 months
        user_logs = models.UserLog.all().order("-time").fetch(31 * 4)

        # Flip 'em around
        user_logs.reverse()

        # Grab deltas
        user_log_last = None
        for user_log in user_logs:
            if user_log_last:
                user_log.delta_registered = user_log.registered_users - user_log_last.registered_users

            user_log.js_month = user_log.time.month - 1
            user_log_last = user_log

        user_logs = filter(lambda user_log: hasattr(user_log, "delta_registered"), user_logs)

        self.render_template("dashboard/users.html", {"user_logs": user_logs})

class RecordStatistics(request_handler.RequestHandler):
    def get(self):
        return self.post()

    def post(self):
        if not users.is_current_user_admin():
            return

        DailyStatistic.record_all()
        self.response.out.write("Dashboard statistics recorded.")

