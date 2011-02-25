import os
from google.appengine.api import users

try:
    import secrets
except:
    class secrets(object):
        facebook_app_id = None
        facebook_app_secret = None
        remote_api_secret = None
        constant_contact_api_key = None
        constant_contact_username = None
        constant_contact_password = None

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

    constant_contact_api_key = secrets.constant_contact_api_key
    constant_contact_username = secrets.constant_contact_username
    constant_contact_password = secrets.constant_contact_password
    
    is_dev_server = False
    if os.environ["SERVER_SOFTWARE"].startswith('Development'):
        is_dev_server = True
    accepts_openid = False
    if not users.create_login_url('/').startswith('https://www.google.com/accounts/ServiceLogin'):
        accepts_openid = True
    if is_dev_server:
        accepts_openid = False # Change to True when we plan to support it on the live server.
    offline_mode = False
     
       
