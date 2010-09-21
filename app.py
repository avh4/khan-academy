import os
import Cookie
import urllib
import logging
from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError
import facebook


from models import UserData

try:
    import secrets
except:
    class secrets(object):
        facebook_app_id = None
        facebook_app_secret = None
        remote_api_secret = None

# A singleton shared across requests
class App(object):
    # This gets reset every time a new version is deployed on
    # a live server.  It has the form major.minor where major
    # is the version specified in app.yaml and minor auto-generated
    # during the deployment process.  Minor is always 1 on a dev
    # server.
    version = os.environ['CURRENT_VERSION_ID']
    # khanacademy.org
    facebook_app_id = secrets.facebook_app_id
    facebook_app_secret = secrets.facebook_app_secret
    remote_api_secret = secrets.remote_api_secret
    
    is_dev_server = False
    if os.environ["SERVER_SOFTWARE"].startswith('Development'):
        is_dev_server = True
    accepts_openid = False
    if not users.create_login_url('/').startswith('https://www.google.com/accounts/ServiceLogin'):
        accepts_openid = True
    if is_dev_server:
        accepts_openid = False # Change to True when we plan to support it on the live server.

"""Returns app.get_current_user() if not None, or a faked User based on the
user's Facebook account if the user has one, or None.
"""
def get_current_user():
    appengine_user = users.get_current_user()
    if appengine_user is not None:
        return appengine_user
    profile = get_facebook_profile()
    if profile is not None:
        # We create a fake user, substituting the user's Facebook uid for their email 
        # and their name for their OpenID identififier since Facebook isn't an
        # OpenID provider at the moment, and GAE displays the OpenID identifier as the nickname().
        return users.User("http://facebookid.khanacademy.org/"+profile["id"], federated_identity = profile["name"])
    
    return None

def get_facebook_profile():
    def get_profile_from_cookie(cookie):
        expires = int(cookie["expires"])
        if expires == 0 and time.time() > expires:
            return None
        memcache_key = "facebook_profile_for_%s" % cookie["access_token"]        
        profile = memcache.get(memcache_key)
        if profile is not None:
            return profile
        try:
            graph = facebook.GraphAPI(cookie["access_token"])
            profile = graph.get_object("me")
            memcache.set(memcache_key, profile)
        except facebook.GraphAPIError, error:
            logging.debug("Ignoring %s.  Assuming access_token is no longer valid." % error)
        return profile

    if App.facebook_app_secret is None:
        return None
    cookies = Cookie.BaseCookie(os.environ.get('HTTP_COOKIE',''))
    morsel_key = "fbs_" + App.facebook_app_id
    morsel = cookies.get(morsel_key)
    if morsel is None:
        return None
    morsel_value = morsel.value
    cookie = facebook.get_user_from_cookie(
        {morsel_key: morsel_value}, App.facebook_app_id, App.facebook_app_secret)
    if cookie:
        return get_profile_from_cookie(cookie)
    return None        

def create_login_url(dest_url):
    return "/login?continue=%s" % urllib.quote(dest_url)
      
class RequestHandler(webapp.RequestHandler):
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
        user = get_current_user()
        if user is not None:
            template_values['username'] = user.nickname()            
        user_data = UserData.get_for(user)
        if user_data is not None:
            template_values['points'] = user_data.points
        template_values['login_url'] = create_login_url(self.request.uri)
        template_values['logout_url'] = users.create_logout_url(self.request.uri)
        path = os.path.join(os.path.dirname(__file__), template_name)
        self.response.out.write(template.render(path, template_values))
        