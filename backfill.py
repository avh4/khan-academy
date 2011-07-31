import logging, itertools

from mapreduce import control
from mapreduce import operation as op

import request_handler
import models
from dashboard.models import RegisteredUserCount

def transfer_user_logs(user_log):
    if RegisteredUserCount().record(val = user_log.registered_users, dt = user_log.time):
        user_log.delete()
    
class StartNewBackfillMapReduce(request_handler.RequestHandler):
    def get(self):
        # Admin-only restriction is handled by /admin/* URL pattern
        # so this can be called by a cron job.

        # Start a new Mapper task.
        mapreduce_id = control.start_map(
                name = "BackfillExerciseOrder",
                handler_spec = "backfill.transfer_user_logs",
                reader_spec = "mapreduce.input_readers.DatastoreInputReader",
                reader_parameters = {"entity_kind": "models.UserLog"},
                shard_count = 64,
                queue_name = "backfill-mapreduce-queue",
                )
        self.response.out.write("OK: " + str(mapreduce_id))
