from phantom_users.phantom_util import is_phantom_id
import facebook_util

def get_nickname_for(user_id,email):
    if not user_id:
        return None

    if facebook_util.is_facebook_user(user_id):
        nickname = facebook_util.get_facebook_nickname(user_id)
    elif is_phantom_id(user_id):
        nickname =  "" # No nickname, results in "Login" in header
    else:
        nickname = email.split('@')[0]
    return nickname
