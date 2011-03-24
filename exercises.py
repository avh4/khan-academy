from google.appengine.api import users

from app import App
import models
import request_handler
import util

class ExerciseAdmin(request_handler.RequestHandler):

    def get(self):
        if not users.is_current_user_admin():
            self.redirect(users.create_login_url(self.request.uri))
            return
        user = util.get_current_user()
        query = models.Exercise.all().order('name')
        exercises = query.fetch(200)

        template_values = {'App' : App, 'exercises': exercises}

        self.render_template('exerciseadmin.html', template_values)


