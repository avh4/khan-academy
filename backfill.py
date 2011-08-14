import logging, itertools

from mapreduce import control
from mapreduce import operation as op

import request_handler
import models
import facebook_util

def check_user_properties(user_data):
    if not user_data or not user_data.user:
        return

    if not user_data.current_user:
        logging.critical("Missing current_user: %s" % user_data.user)

    if not user_data.user_id:
        logging.critical("Missing user_id: %s" % user_data.user)

    if not user_data.user_email:
        logging.critical("Missing user_email: %s" % user_data.user)

    if user_data.current_user.email() != user_data.user_email:
        logging.warning("current_user does not match user_email: %s" % user_data.user)

    if facebook_util.is_facebook_user_id(user_data.user_id) or facebook_util.is_facebook_user_id(user_data.user_email):
        if user_data.user_id != user_data.user_email:
            logging.critical("facebook user's user_id does not match user_email: %s" % user_data.user)

class StartNewBackfillMapReduce(request_handler.RequestHandler):
    def get(self):
        pass

        # Admin-only restriction is handled by /admin/* URL pattern
        # so this can be called by a cron job.

        # Start a new Mapper task.
        # mapreduce_id = control.start_map(
        #     name = "BackfillExerciseOrder",
        #     handler_spec = "backfill.transfer_user_logs",
        #     reader_spec = "mapreduce.input_readers.DatastoreInputReader",
        #     reader_parameters = {"entity_kind": "models.UserLog"},
        #     shard_count = 64,
        #     queue_name = "backfill-mapreduce-queue",
        #   )
        # self.response.out.write("OK: " + str(mapreduce_id))
