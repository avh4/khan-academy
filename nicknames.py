import facebook_util

def get_nickname_for(user):
    if facebook_util.is_facebook_email(user.email()):
        nickname = facebook_util.get_facebook_nickname(user)
    else:
        nickname = user.nickname().split('@')[0]
        nickname = nickname[0].upper() + nickname[1:]
    return nickname
