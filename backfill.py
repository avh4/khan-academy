import logging

from mapreduce import control
from mapreduce import operation as op

import request_handler
import models
import consts
import points

def user_video_update_map(user_video):
    video_points_total = points.VideoPointCalculator(user_video)
    if not user_video.completed and video_points_total >= consts.VIDEO_POINTS_BASE:
        # Just finished this video for the first time
        user_video.completed = True
        yield op.db.Put(user_video)

class StartNewBackfillMapReduce(request_handler.RequestHandler):
    def get(self):
        # Admin-only restriction is handled by /admin/* URL pattern
        # so this can be called by a cron job.
        # Start a new Mapper task for calling statistics_update_map
        mapreduce_id = control.start_map(
                name = "BackfillUserVideo",
                handler_spec = "backfill.user_video_update_map",
                reader_spec = "mapreduce.input_readers.DatastoreInputReader",
                reader_parameters = {"entity_kind": "models.UserVideo"})
        self.response.out.write("OK: " + str(mapreduce_id))


