import facebook_util

def get_nickname_for(user):
    if not user:
        return None

    if facebook_util.is_facebook_email(user.email()):
        nickname = facebook_util.get_facebook_nickname(user)
    else:
        nickname = user.nickname().split('@')[0]

    return nickname
