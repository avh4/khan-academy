import os
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

import util
from app import App
from models import UserData

class RequestHandler(webapp.RequestHandler):

    def request_string(self, key, default = ''):
        return self.request.get(key, default_value=default)

    def request_int(self, key, default = None):
        try:
            return int(self.request_string(key))
        except ValueError:
            if default is not None:
                return default
            else:
                raise # No value available and no default supplied, raise error

    def request_float(self, key, default = None):
        try:        
            return float(self.request_string(key))
        except ValueError:
            if default is not None:
                return default
            else:
                raise # No value available and no default supplied, raise error

    def request_bool(self, key, default = None):
        if default is None:
            return self.request_int(key) == 1
        else:
            return self.request_int(key, 1 if default else 0) == 1

    def handle_exception(self, e, *args):
        if type(e) is CapabilityDisabledError:
            self.response.out.write("<p>The site is temporarily down for maintenance.  Please try again at the start of the next hour.  We apologize for the inconvenience.</p>")
            return
        else:
            return webapp.RequestHandler.handle_exception(self, e, args)

    def render_template(self, template_name, template_values):
        template_values['App'] = App
        template_values['points'] = None
        template_values['username'] = ""
        user = util.get_current_user()
        if user is not None:
            template_values['username'] = user.nickname()            
        user_data = UserData.get_for(user)
        if user_data is not None:
            template_values['points'] = user_data.points
        template_values['login_url'] = util.create_login_url(self.request.uri)
        template_values['logout_url'] = users.create_logout_url(self.request.uri)
        path = os.path.join(os.path.dirname(__file__), template_name)
        self.response.out.write(template.render(path, template_values))
 
