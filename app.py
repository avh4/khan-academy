import datetime
import os
import logging
from stat import ST_MTIME, ST_MODE, S_ISDIR

from google.appengine.api import users

try:
    import secrets
except:
    class secrets(object):
        facebook_app_id = None
        facebook_app_secret = None
        google_consumer_key = None
        google_consumer_secret = None
        remote_api_secret = None
        constant_contact_api_key = None
        constant_contact_username = None
        constant_contact_password = None
        flask_secret_key = None

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

    google_consumer_key = secrets.google_consumer_key
    google_consumer_secret = secrets.google_consumer_secret

    remote_api_secret = secrets.remote_api_secret

    constant_contact_api_key = secrets.constant_contact_api_key
    constant_contact_username = secrets.constant_contact_username
    constant_contact_password = secrets.constant_contact_password

    flask_secret_key = secrets.flask_secret_key
    
    is_dev_server = False
    if os.environ["SERVER_SOFTWARE"].startswith('Development'):
        is_dev_server = True
    accepts_openid = False
    if not users.create_login_url('/').startswith('https://www.google.com/accounts/ServiceLogin'):
        accepts_openid = True
    if is_dev_server:
        accepts_openid = False # Change to True when we plan to support it on the live server.
    offline_mode = False

    # Last modified date of entire app subdirectory. Only to be used in dev server.
    @staticmethod
    def last_modified_date(top = None):

        if not App.is_dev_server:
            raise Exception("last_modified_date should not be called on the production servers")

        if not top:
            top = os.path.abspath(os.path.join(__file__, ".."))

        dt = os.stat(top)[ST_MTIME]

        for f in os.listdir(top):
            pathname = os.path.join(top, f)
            try:
                mode = os.stat(pathname)[ST_MODE]
                if S_ISDIR(mode):
                    # It's a directory, recurse into it
                    dt_subdir = App.last_modified_date(pathname)
                    if dt_subdir > dt:
                        dt = dt_subdir
            except OSError:
                pass

        return dt
