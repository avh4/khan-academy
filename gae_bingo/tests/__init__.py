import logging

from google.appengine.ext.webapp import template, RequestHandler

from gae_bingo.cache import BingoCache
from gae_bingo.config import can_control_experiments

class RunStep(RequestHandler):

    def get(self):

        if not can_control_experiments():
            self.redirect("/")
            return

        step = self.request.get("step")
        v = None

        if step == "delete_all":
            v = self.delete_all_experiments()
        elif step == "participate_in_A":
            v = self.participate_in_monkeys()

        self.response.out.write(v)

    def delete_all_experiments(self):

        bingo_cache = BingoCache.get()
        
        for experiment_name in bingo_cache.experiments:
            bingo_cache.delete_experiment_and_alternatives(bingo_cache.get_experiment(experiment_name))

        return len(bingo_cache.experiments)

    def participate_in_monkeys(self):
        return ab_test("monkeys")
