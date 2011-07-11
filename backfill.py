import logging

from mapreduce import control
from mapreduce import operation as op

import request_handler
import models
import consts
import points
import nicknames
from facebook_util import is_facebook_email

def user_data_current_user_update(user_data):
    if not user_data.current_user:
        user_data.current_user = user_data.user
        yield op.db.Put(user_data)

def feedback_author_nickname_update(feedback):
    if not feedback.author_nickname or is_facebook_email(feedback.author_nickname):
        feedback.author_nickname = nicknames.get_nickname_for(feedback.author)
        yield op.db.Put(feedback)

class StartNewBackfillMapReduce(request_handler.RequestHandler):
    def get(self):
        # Admin-only restriction is handled by /admin/* URL pattern
        # so this can be called by a cron job.

        # Start a new Mapper task.
        mapreduce_id = control.start_map(
                name = "BackfillUserData",
                handler_spec = "backfill.user_data_current_user_update",
                reader_spec = "mapreduce.input_readers.DatastoreInputReader",
                reader_parameters = {"entity_kind": "models.UserData"},
                shard_count = 64,
                queue_name = "backfill-mapreduce-queue",
                )
        self.response.out.write("OK: " + str(mapreduce_id))

        mapreduce_id = control.start_map(
                name = "BackfillFeedback",
                handler_spec = "backfill.feedback_author_nickname_update",
                reader_spec = "mapreduce.input_readers.DatastoreInputReader",
                reader_parameters = {"entity_kind": "discussion.models_discussion.Feedback"},
                shard_count = 64,
                queue_name = "backfill-mapreduce-queue",
                )
        self.response.out.write("OK: " + str(mapreduce_id))
