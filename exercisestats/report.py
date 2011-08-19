import request_handler
import user_util

from itertools import groupby
from models import ProblemLog

class Test(request_handler.RequestHandler):
    @user_util.developer_only
    def get(self):
        problem_log_query = ProblemLog.all()
        problem_logs = problem_log_query.fetch(1000)

        problem_logs.sort(key=lambda log: log.time_taken)
        grouped = dict((k, sum(1 for i in v)) for (k, v) in groupby(problem_logs, key=lambda log: log.time_taken))

        hist = []
        total = sum(grouped[k] for k in grouped)
        cumulative = 0
        for time in range(180):
            count = grouped.get(time, 0)
            cumulative += count
            hist.append({
                'time': time,
                'count': count,
                'cumulative': cumulative,
                'percent': 100.0 * count / total,
                'percent_cumulative': 100.0 * cumulative / total,
                'percent_cumulative_tenth': 10.0 * cumulative / total,
            })

        context = { 'selected_nav_link': 'practice', 'hist': hist, 'total': total }

        self.render_template('exercisestats/test.html', context)
