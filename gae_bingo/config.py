from google.appengine.api import users

# Customize can_see_experiments however you want to specify
# whether or not the currently-logged-in user has access
# to the experiment dashboard.
def can_control_experiments():
    return users.is_current_user_admin()

