import logging, itertools

from mapreduce import control
from mapreduce import operation as op

import request_handler
import models
from dashboard.models import RegisteredUserCount

def update_student_lists(student_list):
    student_list.deleted = student_list.deleted
    yield op.db.Put(student_list)

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
               name = "BackfillExerciseOrder",
               handler_spec = "backfill.update_student_lists",
               reader_spec = "mapreduce.input_readers.DatastoreInputReader",
               reader_parameters = {"entity_kind": "models.StudentList"},
               shard_count = 64,
               queue_name = "backfill-mapreduce-queue",
               )
        self.response.out.write("OK: " + str(mapreduce_id))
