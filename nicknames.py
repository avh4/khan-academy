
import facebook_util

def get_nickname_for(user):
    if not user:
        return None

    if facebook_util.is_facebook_email(user.email()):
        return facebook_util.get_facebook_nickname(user)
    else:
        return user.nickname()


