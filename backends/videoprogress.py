import logging

from google.appengine.api import runtime
from google.appengine.api import backends
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import taskqueue
from google.appengine.ext.webapp.util import run_wsgi_app

from models import UserData, UserVideo

class StartBackfill(webapp.RequestHandler):
    def get(self):
        self.post()
    def post(self):
        MAX_SELECTORS = 100
        self.response.out.write('Backfill started\n')

        user_data = None
        while not runtime.is_shutting_down():
            if user_data is None:
                user_data = UserData.gql("ORDER BY last_login DESC").get()
            else:
                user_data = UserData.gql("WHERE last_login <= :1 " +
                                         "ORDER BY last_login DESC", user_data).get()

            if user_data is None:
                self.response.out.write("Backfill complete\n")
                return

            css_list = ['.vid-progress{background-position:0px 40px;padding:40px;background-repeat:no-repeat;width:20px;height:20px;}']
            query_results = True
            cursor = None

            # Set css for completed videos
            while query_results and not runtime.is_shutting_down():
                user_video_query = UserVideo.gql("WHERE user = :1 AND completed = True", user_data.user)
                if cursor:
                    user_video_query.with_cursor(cursor)

                query_results = False
                for user_video in user_video_query.fetch(MAX_SELECTORS):
                    query_results = True
                    css_list.append('#v'+str(user_video.video.key().id())+',')
                cursor = user_video_query.cursor()
                
                css_list.append('#fakeid1{background-image:url(/images/vid-progress-complete.png);}')

            # Set css for started videos
            while query_results and not runtime.is_shutting_down():
                user_video_query = UserVideo.gql("WHERE user = :1 AND completed = False", user_data.user)
                if cursor:
                    user_video_query.with_cursor(cursor)

                query_results = False
                for user_video in user_video_query.fetch(MAX_SELECTORS):
                    query_results = True
                    css_list.append('#v'+str(user_video.video.key().id())+',')
                cursor = user_video_query.cursor()
                
                css_list.append('#fakeid2{background-image:url(/images/vid-progress-started.png);}')

            UserVideoCss.get_or_insert(
                    key_name=UserVideoCss.key_for(user_data),
                    video_css = ''.join(css_list),
                    user = user_data.user
                    )
            
            logging.info('Completed video_css backfill for %s' % user_data.nickname)

class StartHandler(webapp.RequestHandler):
    '''Handler for /_ah/start' Called when the backend is started.'''
    def get(self):
        logging.critical('Video Css Backend Started')
        self.response.out.write('Ready for Backfill\n')

class BackfillProgressHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write("In progress\n")

def main():
    run_wsgi_app(webapp.WSGIApplication([
        (r'/_ah/start', StartHandler),
        (r'/backends/backfillvideocss', StartBackfill),
        (r'/backends/backfillvideocssprogress', BackfillProgressHandler),
    ]))

if __name__ == '__main__':
    main()
