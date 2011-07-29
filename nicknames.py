from phantom_users.phantom_util import is_phantom_email
import facebook_util

# Now that we're supporting unicode nicknames, ensure all callers get a
# consistent type of object back by converting everything to unicode.
# This fixes issue #4297.
def to_unicode(s):
    if not isinstance(s, unicode):
        return unicode(s, 'utf-8', 'ignore')
    else:
        return s

def get_nickname_for(user):
    if not user:
        return None

    if facebook_util.is_facebook_email(user.email()):
        nickname = facebook_util.get_facebook_nickname(user)
    elif is_phantom_email(user.email()):
        nickname =  "" # No nickname, results in "Login" in header
    else:
        nickname = user.nickname().split('@')[0]

    return to_unicode(nickname)
