import logging, itertools

from mapreduce import control
from mapreduce import operation as op

import request_handler
import models
import facebook_util
from nicknames import get_nickname_for

def cache_user_nickname(user_data):
    if not user_data or not user_data.user:
        return

    current_nickname = get_nickname_for(user_data)
    if user_data.user_nickname != current_nickname:
        user_data.user_nickname = current_nickname
        yield op.db.Put(user_data)

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

def remove_deleted_studentlists(studentlist):
    try:
        deleted = studentlist.deleted
        del studentlist.deleted
        if deleted:
            yield op.db.Delete(studentlist)
        else:
            yield op.db.Put(studentlist)
    except AttributeError:
        pass
        # do nothing, as this studentlist is fine.

class StartNewBackfillMapReduce(request_handler.RequestHandler):
    def get(self):
        # pass

        # Admin-only restriction is handled by /admin/* URL pattern
        # so this can be called by a cron job.

        # Start a new Mapper task.
        mapreduce_id = control.start_map(
            name = "RemoveDeletedStudentlists",
            handler_spec = "backfill.remove_deleted_studentlists",
            reader_spec = "mapreduce.input_readers.DatastoreInputReader",
            reader_parameters = {"entity_kind": "models.StudentList"},
            shard_count = 64,
            queue_name = "backfill-mapreduce-queue",
          )
        self.response.out.write("OK: " + str(mapreduce_id))
