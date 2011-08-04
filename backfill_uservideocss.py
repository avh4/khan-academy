import logging
import pickle

from mapreduce import control
from mapreduce import operation as op

from models import UserData, UserVideo, UserVideoCss
from google.appengine.ext.db import ReferencePropertyResolveError

def backfill_user_data(user_data):
    batch_size = 1000
    query_results = True
    cursor = None

    if not user_data or not user_data.user:
        return

    user_video_css = UserVideoCss.get_for_user_data(user_data)
    css_dict = {'started': set([]), 'completed': set([])}

    # Set css for completed videos
    while query_results:
        user_video_query = UserVideo.gql("WHERE user = :1 AND completed = True",
                                         user_data.user)
        if cursor:
            user_video_query.with_cursor(cursor)

        query_results = False
        for user_video in user_video_query.fetch(batch_size):
            query_results = True

            video_key = UserVideo.video.get_value_for_datastore(user_video)
            css_dict['completed'].add('.v'+str(video_key.id()))

        cursor = user_video_query.cursor()

    query_results = True
    cursor = None
        
    # Set css for started videos
    while query_results:
        user_video_query = UserVideo.gql("WHERE user = :1 AND completed = False", 
                                         user_data.user)
        if cursor:
            user_video_query.with_cursor(cursor)

        query_results = False
        for user_video in user_video_query.fetch(batch_size):
            query_results = True

            video_key = UserVideo.video.get_value_for_datastore(user_video)
            css_dict['started'].add('.v'+str(video_key.id()))

        cursor = user_video_query.cursor()

    if len(css_dict['started']) or len(css_dict['completed']):
        user_video_css.pickled_dict = pickle.dumps(css_dict)
        user_video_css.load_pickled()
        user_video_css.version += 1
        yield op.db.Put(user_video_css)
        
    logging.info('Completed video_css backfill for %s' % user_data.user)
