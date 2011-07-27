import logging

import request_handler
import models

class Dashboard(request_handler.RequestHandler):

    def get(self):
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

