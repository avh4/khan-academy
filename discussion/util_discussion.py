from google.appengine.api import users
from models import UserData

def is_current_user_moderator():
    return users.is_current_user_admin() or UserData.get_for_current_user().moderator

def is_honeypot_empty(request):
    return not request.get("honey_input") and not request.get("honey_textarea")
