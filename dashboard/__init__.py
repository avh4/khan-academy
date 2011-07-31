import logging

from google.appengine.api import users

import request_handler
from dashboard.models import DailyStatistic, RegisteredUserCount

class Dashboard(request_handler.RequestHandler):

    def get(self):
        if not users.is_current_user_admin():
            self.redirect(users.create_login_url(self.request.uri))
            return

        # Grab last ~4 months
        user_counts = RegisteredUserCount.all().order("-dt").fetch(31 * 4)

        # Flip 'em around
        user_counts.reverse()

        # Grab deltas
        user_count_last = None
        for user_count in user_counts:
            if user_count_last:
                user_count.delta_registered = user_count.val - user_count_last.val

            user_count.js_month = user_count.dt.month - 1
            user_count_last = user_count

        user_counts = filter(lambda user_count: hasattr(user_count, "delta_registered"), user_counts)

        self.render_template("dashboard/users.html", {"user_counts": user_counts})

class RecordStatistics(request_handler.RequestHandler):
    def get(self):
        return self.post()

    def post(self):
        if not users.is_current_user_admin():
            return

        DailyStatistic.record_all()
        self.response.out.write("Dashboard statistics recorded.")

