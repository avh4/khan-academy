import datetime
import logging

from google.appengine.api import users

from app import App
import request_handler
from dashboard.models import DailyStatistic, RegisteredUserCount, ProblemLogCount

class Dashboard(request_handler.RequestHandler):

    def get(self):
        if not users.is_current_user_admin():
            if App.dashboard_secret and self.request_string("x", default=None) != App.dashboard_secret:
                logging.critical(App.dashboard_secret)
                self.redirect(users.create_login_url(self.request.uri))
                return

        context = {}
        context.update(daily_graph_context(RegisteredUserCount, "user_counts"))
        context.update(daily_graph_context(ProblemLogCount, "problem_counts"))

        self.render_template("dashboard/dashboard.html", context)

def daily_graph_context(cls, key):
    # Grab last ~4 months
    counts = cls.all().order("-dt").fetch(31 * 4)

    # Flip 'em around
    counts.reverse()

    # Grab deltas
    count_last = None
    for count in counts:
        if count_last:
            count.delta = count.val - count_last.val

        # Better to show date previous to date stat recorded.
        count.dt_display = count.dt - datetime.timedelta(days=1)
        count.js_month = count.dt_display.month - 1
        count_last = count

    return { key: filter(lambda count: hasattr(count, "delta"), counts) }

class RecordStatistics(request_handler.RequestHandler):
    def get(self):
        return self.post()

    def post(self):
        if not users.is_current_user_admin():
            return

        DailyStatistic.record_all()
        self.response.out.write("Dashboard statistics recorded.")

