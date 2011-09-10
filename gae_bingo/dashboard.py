import logging
import os

from google.appengine.ext.webapp import template, RequestHandler

from .cache import BingoCache
from .stats import describe_result_in_words
from .config import can_control_experiments

class Dashboard(RequestHandler):

    def get(self):

        if not can_control_experiments():
            self.redirect("/")
            return

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

class EndExperiment(RequestHandler):

    def post(self):

        if not can_control_experiments():
            return

        experiment_name = self.request.get("experiment_name")
        alternative_number = int(self.request.get("alternative_number"))

        if not experiment_name:
            return

        bingo_cache = BingoCache.get()

        experiment = bingo_cache.get_experiment(experiment_name)

        if not experiment:
            return

        # Need to end all experiments that may have been kicked off
        # by an experiment with multiple conversions
        experiments, alternative_lists = bingo_cache.experiments_and_alternatives_from_canonical_name(experiment.canonical_name)

        if not experiments or not alternative_lists:
            return

        for i in range(len(experiments)):
            experiment, alternatives = experiments[i], alternative_lists[i]

            alternative_chosen = filter(lambda alternative: alternative.number == alternative_number , alternatives)

            if len(alternative_chosen) == 1:
                experiment.live = False
                experiment.set_short_circuit_content(alternative_chosen[0].content)
                bingo_cache.update_experiment(experiment)

        self.redirect("/gae_bingo/dashboard")
