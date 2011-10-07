import logging, itertools

from mapreduce import control
from mapreduce import operation as op

import request_handler
import models
import facebook_util
from nicknames import get_nickname_for

from google.appengine.ext import db

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

def dedupe_related_videos(exercise):
    exvids = exercise.related_videos_query().fetch(100)
    video_keys = set()
    for exvid in exvids:
        video_key = exvid.video.key()
        if video_key in video_keys:
            logging.critical("Deleting ExerciseVideo for %s, %s",
                exercise.name,
                video_key.id_or_name())
            yield op.db.Delete(exvid)
        else:
            video_keys.add(video_key)

def migrate_userdata(key):
    def tn(key):
        user_data = db.get(key)
        # remove blank entries if present
        user_data.all_proficient_exercises.remove('')
        user_data.proficient_exercises.remove('')
        user_data.badges.remove('')
        user_data.put()
    db.run_in_transaction(tn, key)

class StartNewBackfillMapReduce(request_handler.RequestHandler):
    def get(self):
        # pass

        # Admin-only restriction is handled by /admin/* URL pattern
        # so this can be called by a cron job.

        # Start a new Mapper task.
        mapreduce_id = control.start_map(
            name="migrate_userdata",
            handler_spec="backfill.migrate_userdata",
            reader_spec="mapreduce.input_readers.DatastoreKeyInputReader",
            reader_parameters={
                "entity_kind": "models.UserData",
                "processing_rate": 200,
            },
            shard_count=64,
            queue_name="backfill-mapreduce-queue",
          )
        self.response.out.write("OK: " + str(mapreduce_id))

def transactional_entity_put(entity_key):
    def entity_put(entity_key):
        entity = db.get(entity_key)
        entity.put()
    db.run_in_transaction(entity_put, entity_key)

class BackfillEntity(request_handler.RequestHandler):
    def get(self):
        entity = self.request_string("kind")
        if not entity:
            self.response.out.write("Must provide kind")
            return

        mapreduce_id = control.start_map(
            name="Put all UserData entities",
            handler_spec="backfill.transactional_entity_put",
            reader_spec="mapreduce.input_readers.DatastoreKeyInputReader",
            reader_parameters={
                "entity_kind": entity,
                "processing_rate": 200
            },
            shard_count=64,
            queue_name="backfill-mapreduce-queue",
          )
        self.response.out.write("OK: " + str(mapreduce_id))
