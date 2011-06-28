from functools import wraps

def data_migration(method):
    '''Redirects users if their data is being migrated.'''

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        user_data = UserData.get_for_current_user()

        if user_data.in_migration:
            self.redirect('/transferaccount')
        else:
            method(self, *args, **kwargs)
    return wrapper

from models import UserData
