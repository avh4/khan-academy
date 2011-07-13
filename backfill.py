import logging, itertools

from mapreduce import control
from mapreduce import operation as op

import request_handler
import models
import consts
import points
import nicknames
from facebook_util import is_facebook_email
    
class StartNewBackfillMapReduce(request_handler.RequestHandler):
    def get(self):
        pass
        # Admin-only restriction is handled by /admin/* URL pattern
        # so this can be called by a cron job.

        # Start a new Mapper task.
        # mapreduce_id = control.start_map(
        #         name = "BackfillExerciseOrder",
        #         handler_spec = "backfill.order_related_videos",
        #         reader_spec = "mapreduce.input_readers.DatastoreInputReader",
        #         reader_parameters = {"entity_kind": "models.Exercise"},
        #         shard_count = 64,
        #         queue_name = "backfill-mapreduce-queue",
        #         )
        # self.response.out.write("OK: " + str(mapreduce_id))
