import urllib
from google.appengine.api import users

import facebook_util

"""Returns users.get_current_user() if not None, or a faked User based on the
user's Facebook account if the user has one, or None.
"""
def get_current_user():

    appengine_user = users.get_current_user()

    if appengine_user is not None:
        return appengine_user

    facebook_user = facebook_util.get_current_facebook_user()

    if facebook_user is not None:
        return facebook_user   

    return None

def get_nickname_for(user):
    if facebook_util.is_facebook_email(user.email()):
        return facebook_util.get_facebook_nickname(user)
    else:
        return user.nickname()

def create_login_url(dest_url):
    return "/login?continue=%s" % urllib.quote(dest_url)
