import unregistered_util
import facebook_util

def get_nickname_for(user):
    if facebook_util.is_facebook_email(user.email()):
        return facebook_util.get_facebook_nickname(user)
    elif unregistered_util.is_phantom_email(user.email()):
        return "" # No nickname, results in "Login" in header
    else:
        return user.nickname()
