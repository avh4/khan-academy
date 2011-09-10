import os
import logging
import simplejson

from google.appengine.ext.webapp import template, RequestHandler

from gae_bingo.gae_bingo import ab_test, bingo
from gae_bingo.cache import BingoCache, BingoIdentityCache
from gae_bingo.config import can_control_experiments
from gae_bingo.dashboard import ControlExperiment

class RunStep(RequestHandler):

    def get(self):

        if not os.environ["SERVER_SOFTWARE"].startswith('Development'):
            return

        step = self.request.get("step")
        v = None

        if step == "delete_all":
            v = self.delete_all_experiments()
        if step == "refresh_identity_record":
            v = self.refresh_identity_record()
        elif step == "participate_in_monkeys":
            v = self.participate_in_monkeys()
        elif step == "participate_in_gorillas":
            v = self.participate_in_gorillas()
        elif step == "participate_in_chimpanzees":
            v = self.participate_in_chimpanzees()
        elif step == "convert_in":
            v = self.convert_in()
        elif step == "count_participants_in":
            v = self.count_participants_in()
        elif step == "count_conversions_in":
            v = self.count_conversions_in()
        elif step == "count_experiments":
            v = self.count_experiments()

        self.response.out.write(simplejson.dumps(v))

    def delete_all_experiments(self):
        bingo_cache = BingoCache.get()
        
        for experiment_name in bingo_cache.experiments.keys():
            bingo_cache.delete_experiment_and_alternatives(bingo_cache.get_experiment(experiment_name))

        return len(bingo_cache.experiments)

    def refresh_identity_record(self):
        BingoIdentityCache.get().load_from_datastore()
        return True

    def participate_in_monkeys(self):
        return ab_test("monkeys")

    def participate_in_gorillas(self):
        return ab_test("gorillas", ["a", "b", "c"])

    def participate_in_chimpanzees(self):
        return ab_test("chimpanzees", conversion_name=["chimps_conversion_1, chimps_conversion_2"])

    def participate_in_crocodiles(self):
        # Weighted test
        return ab_test("crocodiles", {"a": 100, "b": 200, "c": 400, "d": 800, "e": 1600})

    def convert_in(self):
        bingo(self.request.get("conversion_name"))
        return True

    def end_and_choose(self):
        bingo_cache = BingoCache.get()
        experiment = bingo_cache.get_experiment(self.request.get("experiment_name"))
        ControlExperiment.choose_alternative(self, experiment)

    def count_participants_in(self):
        return reduce(lambda a, b: a + b, 
                map(lambda alternative: alternative.participants, 
                    BingoCache.get().get_alternatives(self.request.get("experiment_name"))
                    )
                )

    def count_conversions_in(self):
        dict_conversions = {}

        for alternative in BingoCache.get().get_alternatives(self.request.get("experiment_name")):
            dict_conversions[alternative.number] = alternative.conversions

        return dict_conversions

    def count_experiments(self):
        return len(BingoCache.get().experiments)
