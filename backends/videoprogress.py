import logging

from google.appengine.api import runtime
from google.appengine.api import backends
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import taskqueue
from google.appengine.ext.webapp.util import run_wsgi_app

from models import UserData, UserVideo

def _get_taskqueue_target():
    #return '%d.%s' % (backends.get_instance(), backends.get_backend())
    return '%s.%d' % (backends.get_backend(), backends.get_instance())

class BackfillProgressHandler(webapp.RequestHandler):
    def get(self):
        logging.critical('here1')
        self.response.out.write('In Progress')
    def post(self):
        logging.critical('here2')
        self.response.out.write('Backfill started')
        while True:
            user_query = db.GqlQuery("SELECT * FROM UserData WHERE video_css = :1", 
                                     '')
            user_data = user_query.get()
            if not user_data:
                self.response.out.write("Backfill complete")
                return

            css_list = ['.vid-progress {background-position: 0px 40px; padding: 40px; background-repeat: no-repeat; width: 20px; height: 20px;}']
            query_results = True
            cursor = None

            while query_results and not runtime.is_shutting_down():
                user_video_query = db.GqlQuery("SELECT * FROM UserVideo " +
                    "WHERE user = :1", user_data.user)
                if cursor:
                    user_video_query.with_cursor(cursor)

                query_results = False
                for user_video in user_video_query.fetch(250):
                    if user_video.completed:
                        url = '/images/vid-progress-complete.png'
                    else:
                        url = '/images/vid-progress-started.png'
                    query_results = True
                    css = ' #id-' + user_video.video.youtube_id + \
                          '{background-image: url(\'' + url + '\');}'
                    css_list.append(css)
                cursor = user_video_query.cursor()

            user_data.video_css = ''.join(css_list)
            user_data.put()

            logging.info('Completed video_css backfill for %s' % user_data.nickname)

class StartHandler(webapp.RequestHandler):
    '''Handler for /_ah/start' Called when the backend is started.'''
    def get(self):
        logging.critical('here3')
        target = _get_taskqueue_target()
        logging.critical(target)
        taskqueue.add(url='/backends/backfillvideoprogress',
                      #target=target,
                      queue_name='backfillvideoprogress-queue')
        self.response.out.write('Backfill Started')

class StopHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write("I haven't written this yet")

def main():
    run_wsgi_app(webapp.WSGIApplication([
        ('/_ah/start', StartHandler),
        ('/backends/backfillvideoprogress', BackfillProgressHandler),
    ]))

if __name__ == '__main__':
    main()
