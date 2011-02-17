import logging

from mapreduce import control
from mapreduce import operation as op

import request_handler
import models
import consts
import points

def user_exercise_update_map(user_exercise):
    if not models.UserExercise.exercise_model.get_value_for_datastore(user_exercise):
        user_exercise.exercise_model = models.Exercise.get_by_name(user_exercise.exercise)
        yield op.db.Put(user_exercise)

class StartNewBackfillMapReduce(request_handler.RequestHandler):
    def get(self):
        # Admin-only restriction is handled by /admin/* URL pattern
        # so this can be called by a cron job.
        # Start a new Mapper task for calling statistics_update_map
        mapreduce_id = control.start_map(
                name = "BackfillUserExercise",
                handler_spec = "backfill.user_exercise_update_map",
                reader_spec = "mapreduce.input_readers.DatastoreInputReader",
                reader_parameters = {"entity_kind": "models.UserExercise"},
                shard_count = 64)
        self.response.out.write("OK: " + str(mapreduce_id))


