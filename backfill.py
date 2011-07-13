import logging, itertools

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

def order_related_videos(exercise):
    #Start ordering
    ExerciseVideos = models.ExerciseVideo.all().filter('exercise =', exercise.key()).fetch(1000)
    playlists = []
    for exercise_video in ExerciseVideos:
        playlists.append(models.VideoPlaylist.get_cached_playlists_for_video(exercise_video.video))

    if playlists:
    
        playlists = list(itertools.chain(*playlists))
        titles = map(lambda pl: pl.title, playlists)
        playlist_sorted = []
        for p in playlists:
            playlist_sorted.append([p, titles.count(p.title)])
        playlist_sorted.sort(key = lambda p: p[1])
        playlist_sorted.reverse()
        playlists = []
        for p in playlist_sorted:
            playlists.append(p[0])
        playlist_dict = {}
        exercise_list = []
    
        for p in playlists:
            playlist_dict[p.title]=[]
            for exercise_video in ExerciseVideos:
                if p.title  in map(lambda pl: pl.title, models.VideoPlaylist.get_cached_playlists_for_video(exercise_video.video)):
                    playlist_dict[p.title].append(exercise_video)

            if playlist_dict[p.title]:
                playlist_dict[p.title].sort(key = lambda e: models.VideoPlaylist.all().filter('video =', e.video).filter('playlist =',p).get().video_position)
                exercise_list.append(playlist_dict[p.title])

        if exercise_list:
            exercise_list = list(itertools.chain(*exercise_list))
            for e in exercise_list:
                e.exercise_order = exercise_list.index(e)
                yield op.db.Put(e) #e.put()
    
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
        
        
        mapreduce_id = control.start_map(
                name = "BackfillExerciseOrder",
                handler_spec = "backfill.order_related_videos",
                reader_spec = "mapreduce.input_readers.DatastoreInputReader",
                reader_parameters = {"entity_kind": "models.Exercise"},
                shard_count = 64,
                queue_name = "backfill-mapreduce-queue",
                )
        self.response.out.write("OK: " + str(mapreduce_id))
