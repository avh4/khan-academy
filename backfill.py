import logging

from mapreduce import control
from mapreduce import operation as op

import request_handler
import models
import consts
import points

def exercise_update_map(exercise):
    exercise.live = True
    yield op.db.Put(exercise)

class StartNewBackfillMapReduce(request_handler.RequestHandler):
    def get(self):
        # Admin-only restriction is handled by /admin/* URL pattern
        # so this can be called by a cron job.
        # Start a new Mapper task for calling statistics_update_map
        mapreduce_id = control.start_map(
                name = "BackfillUserExercise",
                handler_spec = "backfill.exercise_update_map",
                reader_spec = "mapreduce.input_readers.DatastoreInputReader",
                reader_parameters = {"entity_kind": "models.Exercise"},
                shard_count = 64,
                queue_name = "backfill-mapreduce-queue",
                )
        self.response.out.write("OK: " + str(mapreduce_id))


