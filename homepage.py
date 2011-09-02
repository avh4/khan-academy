import random

import consts
import library
import request_handler
import models
import layer_cache
from topics_list import DVD_list

@layer_cache.cache(layer=layer_cache.Layers.InAppMemory)
def new_and_noteworthy_link_sets():

    playlist = models.Playlist.all().filter("title =", "New and Noteworthy").get()
    if not playlist:
        return []

    videos = models.VideoPlaylist.get_cached_videos_for_playlist(playlist)
    exercises = []

    # We use playlist tags to identify new and noteworthy exercises
    # just so Sal has a really simple, fast, all-YouTube interface
    playlist.tags = ['addition_1', 'measuring_angles']
    for tag in playlist.tags:
        exercise = models.Exercise.get_by_name(tag)
        if exercise:
            exercises.append(exercise)

    items_per_set = 4

    sets = []
    current_set = []
    current_set_exercise_position = random.randint(0, items_per_set - 1)

    for video in videos:

        if len(current_set) >= items_per_set:
            sets.append(current_set)
            current_set = []
            current_set_exercise_position = random.randint(0, items_per_set - 1)

        if len(exercises) > 0 and len(current_set) == current_set_exercise_position:
            exercise = exercises.pop(0)

            current_set.append({
                "href": exercise.ka_url,
                "thumb_url": "/images/screenshot-tour/problems.png",
                "desc": exercise.display_name,
                "youtube_id": "",
                "selected": False,
                "key": exercise.key,
            })

        if len(current_set) >= items_per_set:
            sets.append(current_set)
            current_set = []
            current_set_exercise_position = random.randint(0, items_per_set - 1)

        current_set.append({
            "href": video.ka_url,
            "thumb_url": video.youtube_thumbnail_url(),
            "desc": video.title,
            "youtube_id": video.youtube_id,
            "selected": False,
            "key": video.key()
        })

    if len(current_set) > 0:
        sets.append(current_set)

    return sets

class ViewHomePage(request_handler.RequestHandler):

    def get(self):

        thumbnail_link_sets = new_and_noteworthy_link_sets()

        # Highlight video #1 from the first set of off-screen thumbnails
        selected_thumbnail = filter(lambda item: len(item["youtube_id"]) > 0, thumbnail_link_sets[1])[0]
        selected_thumbnail["selected"] = True

        # Get pregenerated library content from our in-memory/memcache two-layer cache
        library_content = library.library_content_html()

        template_values = {
                            'video_id': selected_thumbnail["youtube_id"],
                            'video_key': selected_thumbnail["key"],
                            'thumbnail_link_sets': thumbnail_link_sets,
                            'library_content': library_content,
                            'DVD_list': DVD_list,
                            'is_mobile_allowed': True,
                            'approx_vid_count': consts.APPROX_VID_COUNT,
                        }
        self.render_template('homepage.html', template_values)
