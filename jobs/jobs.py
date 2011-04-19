import request_handler

class FullTimeDeveloper(request_handler.RequestHandler):

    ACTIVE = True

    def get(self):
        if self.ACTIVE:
            self.render_template("jobs/fulltime_developer.html", {})
        else:
            self.render_template("jobs/no_longer_available.html", {})
