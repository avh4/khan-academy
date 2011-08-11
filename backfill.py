import logging, itertools

from mapreduce import control
from mapreduce import operation as op

import request_handler
import models
from dashboard.models import RegisteredUserCount

def add_user_id(user_data):
    if not user_data or not user_data.current_user:
        return
        
    user = user_data.current_user
    if user_data.user_id and user_data.user_email:
        return
    user_id = user.user_id()
    if user_id:
        user_data.user_id = "http://googleid.khanacademy.org/"+user_id
        user_data.user_email = user.email()
    else:
        user_data.user_id = user_data.email
        user_data.user_email = user.email()
    yield op.db.Put(user_data)

class StartNewBackfillMapReduce(request_handler.RequestHandler):
    def get(self):
        # pass
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
        
        mapreduce_id = control.start_map(
               name = "BackfillAddUserID",
               handler_spec = "backfill.add_user_id",
               reader_spec = "mapreduce.input_readers.DatastoreInputReader",
               reader_parameters = {"entity_kind": "models.UserData"},
               shard_count = 64,
               queue_name = "backfill-mapreduce-queue",
               )
        self.response.out.write("OK: " + str(mapreduce_id))
