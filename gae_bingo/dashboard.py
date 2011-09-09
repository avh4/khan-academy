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

            experiment = bingo_cache.get_experiment(experiment_name)
            alternatives = bingo_cache.get_alternatives(experiment_name)

            experiment_results.append([
                experiment,
                alternatives,
                reduce(lambda a, b: a + b, map(lambda alternative: alternative.participants, alternatives)),
                reduce(lambda a, b: a + b, map(lambda alternative: alternative.conversions, alternatives)),
                describe_result_in_words(alternatives),
            ])

        experiment_results = sorted(experiment_results, key=lambda results: results[0].name)

        self.response.out.write(
            template.render(path, {
                "experiment_results": experiment_results,
            })
        )
