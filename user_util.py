from functools import wraps

from google.appengine.api import users

import models

def admin_only(method):
    '''Decorator that requires a admin account.'''

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if users.is_current_user_admin():
            return method(self, *args, **kwargs)
        else:
            url = users.create_login_url(self.request.uri)

            if users.get_current_user:
                url = users.create_logout_url(url)

            self.redirect(url)
            return

    return wrapper

def is_current_user_developer():
    user_data = models.UserData.current()
    return bool(users.is_current_user_admin() or (user_data and user_data.developer))

def developer_only(method):
    '''Decorator that requires a developer account.'''

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if is_current_user_developer():
            return method(self, *args, **kwargs)
        else:
            url = users.create_login_url(self.request.uri)

            if users.get_current_user():
                url = users.create_logout_url(url)

            self.redirect(url)
            return

    return wrapper

