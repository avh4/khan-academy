import random

from django.template.defaultfilters import escape

import consts
import library
import request_handler
import models
import layer_cache
import templatetags
from topics_list import DVD_list

def thumbnail_link_dict(video = None, exercise = None, thumb_url = None):

    link_dict = None

    if video:
        link_dict = {
            "href": video.ka_url,
            "thumb_url": video.youtube_thumbnail_url(),
            "desc_html": templatetags.video_name_and_progress(video),
            "teaser_html": video.description,
            "youtube_id": video.youtube_id,
            "selected": False,
            "key": video.key(),
            "type": "video",
        }

    if exercise:
        link_dict = {
            "href": exercise.ka_url,
            "thumb_url": thumb_url,
            "desc_html": escape(exercise.display_name),
            "teaser_html": "Exercise your <em>%s</em> skills" % escape(exercise.display_name),
            "youtube_id": "",
            "selected": False,
            "key": exercise.key,
            "type": "exercise",
        }

    if link_dict:

        if len(link_dict["teaser_html"]) > 60:
            link_dict["teaser_html"] = link_dict["teaser_html"][:60] + "&hellip;"

        return link_dict

    return None

@layer_cache.cache(layer=layer_cache.Layers.InAppMemory, expiration=60*60*24) # Expire daily
def new_and_noteworthy_link_sets():

    playlist = models.Playlist.all().filter("title =", "New and Noteworthy").get()
    if not playlist:
        # If we can't find the playlist, just show the default TED talk.
        return []

    videos = models.VideoPlaylist.get_cached_videos_for_playlist(playlist)
    if len(videos) < 2:
        # If there's only one video, don't bother.
        return []

    exercises = []

    # We use playlist tags to identify new and noteworthy exercises
    # just so Sal has a really simple, fast, all-YouTube interface
    for tag in playlist.tags:
        exercise = models.Exercise.get_by_name(tag)
        if exercise:
            exercises.append(exercise)

    if len(exercises) == 0:
        # Temporary hard-coding of a couple exercises until Sal picks a few
        playlist.tags = ['solid_geometry', 'estimation_with_decimals', 'multiplication_4']
        for tag in playlist.tags:
            exercise = models.Exercise.get_by_name(tag)
            if exercise:
                exercises.append(exercise)

    items_per_set = 4

    sets = []
    current_set = []
    current_set_exercise_position = random.randint(0, items_per_set - 1)
    next_exercise = 0

    exercise_icon_files = ["ex1.png", "ex2.png", "ex3.png", "ex4.png"]
    random.shuffle(exercise_icon_files)

    for video in videos:

        if len(current_set) >= items_per_set:
            sets.append(current_set)
            current_set = []
            current_set_exercise_position = random.randint(0, items_per_set - 1)

        if next_exercise < len(exercises) and len(current_set) == current_set_exercise_position:
            exercise = exercises[next_exercise]

            thumb_url = "/images/splashthumbnails/exercises/%s" % (exercise_icon_files[next_exercise % (len(exercise_icon_files))])
            current_set.append(thumbnail_link_dict(exercise = exercise, thumb_url = thumb_url))

            next_exercise += 1

        if len(current_set) >= items_per_set:
            sets.append(current_set)
            current_set = []
            current_set_exercise_position = random.randint(0, items_per_set - 1)

        current_set.append(thumbnail_link_dict(video = video))

    if len(current_set) > 0:
        sets.append(current_set)

    return sets

class ViewHomePage(request_handler.RequestHandler):

    def get(self):

        thumbnail_link_sets = new_and_noteworthy_link_sets()

        # If all else fails, just show the TED talk on the homepage
        video_id, video_key = "gM95HHI4gLk", ""

        # If possible, highlight video #1 from the first set of off-screen thumbnails
        if len(thumbnail_link_sets) > 1 and len(thumbnail_link_sets[1]) > 0:

            selected_thumbnail = filter(lambda item: len(item["youtube_id"]) > 0, thumbnail_link_sets[1])[0]
            selected_thumbnail["selected"] = True

            video_id = selected_thumbnail["youtube_id"]
            video_key = selected_thumbnail["key"]

        # Get pregenerated library content from our in-memory/memcache two-layer cache
        library_content = library.library_content_html()

        template_values = {
                            'video_id': video_id,
                            'video_key': video_key,
                            'thumbnail_link_sets': thumbnail_link_sets,
                            'library_content': library_content,
                            'DVD_list': DVD_list,
                            'is_mobile_allowed': True,
                            'approx_vid_count': consts.APPROX_VID_COUNT,
                        }
        self.render_template('homepage.html', template_values)
