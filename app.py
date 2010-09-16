import os
from google.appengine.api import users

# A singleton shared across requests
class App(object):
    # This gets reset every time a new version is deployed on
    # a live server.  It has the form major.minor where major
    # is the version specified in app.yaml and minor auto-generated
    # during the deployment process.  Minor is always 1 on a dev
    # server.
    version = os.environ['CURRENT_VERSION_ID']
    if os.environ["SERVER_SOFTWARE"].startswith('Development'):
        is_dev_server = True
    if not users.create_login_url('/').startswith('https://www.google.com/accounts/ServiceLogin'):
        accepts_openid = True
        
