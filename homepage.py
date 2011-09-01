import random
from topics_list import DVD_list

import consts
import library
import request_handler

class ViewHomePage(request_handler.RequestHandler):
    def get(self):
        thumbnail_link_sets = [
            [
                {
                    "href": "/video/khan-academy-on-the-gates-notes",
                    "class": "thumb-gates_thumbnail",
                    "desc": "Khan Academy on the Gates Notes",
                    "youtube_id": "UuMTSU9DcqQ",
                    "selected": False,
                },
                {
                    "href": "http://www.youtube.com/watch?v=dsFQ9kM1qDs",
                    "class": "thumb-overview_thumbnail",
                    "desc": "Overview of our video library",
                    "youtube_id": "dsFQ9kM1qDs",
                    "selected": False,
                },
                {
                    "href": "/video/salman-khan-speaks-at-gel--good-experience-live--conference",
                    "class": "thumb-gel_thumbnail",
                    "desc": "Sal Khan talk at GEL 2010",
                    "youtube_id": "yTXKCzrFh3c",
                    "selected": False,
                },
                {
                    "href": "/video/khan-academy-on-pbs-newshour--edited",
                    "class": "thumb-pbs_thumbnail",
                    "desc": "Khan Academy on PBS NewsHour",
                    "youtube_id": "4jXv03sktik",
                    "selected": False,
                },
            ],
            [
                {
                    "href": "http://www.ted.com/talks/salman_khan_let_s_use_video_to_reinvent_education.html",
                    "class": "thumb-ted_thumbnail",
                    "desc": "Sal on the Khan Academy @ TED",
                    "youtube_id": "gM95HHI4gLk",
                    "selected": False,
                },
                {
                    "href": "http://www.youtube.com/watch?v=p6l8-1kHUsA",
                    "class": "thumb-tech_award_thumbnail",
                    "desc": "What is the Khan Academy?",
                    "youtube_id": "p6l8-1kHUsA",
                    "selected": False,
                },
                {
                    "href": "/video/khan-academy-exercise-software",
                    "class": "thumb-exercises_thumbnail",
                    "desc": "Overview of our exercise software",
                    "youtube_id": "hw5k98GV7po",
                    "selected": False,
                },
                {
                    "href": "/video/forbes--names-you-need-to-know---khan-academy",
                    "class": "thumb-forbes_thumbnail",
                    "desc": "Forbes Names You Need To Know",
                    "youtube_id": "UkfppuS0Plg",
                    "selected": False,
                },
            ]
        ]

        random.shuffle(thumbnail_link_sets)

        # Highlight video #1 from the first set of off-screen thumbnails
        selected_thumbnail = thumbnail_link_sets[1][0]
        selected_thumbnail["selected"] = True
        movie_youtube_id = selected_thumbnail["youtube_id"]

        # Get pregenerated library content from our in-memory/memcache two-layer cache
        library_content = library.library_content_html()

        template_values = {
                            'video_id': movie_youtube_id,
                            'thumbnail_link_sets': thumbnail_link_sets,
                            'library_content': library_content,
                            'DVD_list': DVD_list,
                            'is_mobile_allowed': True,
                            'approx_vid_count': consts.APPROX_VID_COUNT,
                        }
        self.render_template('homepage.html', template_values)
