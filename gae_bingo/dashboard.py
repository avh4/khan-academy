import logging
import os

from google.appengine.ext.webapp import template, RequestHandler

from .cache import BingoCache
from .stats import describe_result_in_words

class Dashboard(RequestHandler):

    def get(self):

        # TODO: restrict access

        path = os.path.join(os.path.dirname(__file__), "templates/dashboard.html")

        bingo_cache = BingoCache.get()

        experiment_results = []
        for experiment_name in bingo_cache.experiments:
            experiment_results.append([
                bingo_cache.get_experiment(experiment_name),
                bingo_cache.get_alternatives(experiment_name),
                describe_result_in_words(bingo_cache.get_alternatives(experiment_name)),
            ])

        experiment_results = sorted(experiment_results, key=lambda results: results[0].name)

        self.response.out.write(
            template.render(path, {
                "experiment_results": experiment_results,
            })
        )
