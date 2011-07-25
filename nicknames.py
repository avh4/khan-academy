from phantom_users.phantom_util import is_phantom_email
import facebook_util

def get_nickname_for(user):
    if not user:
        return None

    if facebook_util.is_facebook_email(user.email()):
        nickname = facebook_util.get_facebook_nickname(user)
    elif is_phantom_email(user.email()):
        nickname =  "" # No nickname, results in "Login" in header
    else:
        nickname = "Google"

    return nickname
