import logging, itertools

from mapreduce import control
from mapreduce import operation as op

import request_handler
import models
import consts
import points
import nicknames
from facebook_util import is_facebook_user

def user_data_properties(user_data):
    if user_data:
        yield op.db.Put(user_data)

    
class StartNewBackfillMapReduce(request_handler.RequestHandler):
    def get(self):
        # Admin-only restriction is handled by /admin/* URL pattern
        # so this can be called by a cron job.

        # Start a new Mapper task.
        mapreduce_id = control.start_map(
                        name = "BackfillUserProperties",
                        handler_spec = "backfill.user_data_properties",
                        reader_spec = "mapreduce.input_readers.DatastoreInputReader",
                        reader_parameters = {"entity_kind": "models.UserData"},
                        shard_count = 64,
                        queue_name = "backfill-mapreduce-queue",
                        )
        self.response.out.write("OK: " + str(mapreduce_id))