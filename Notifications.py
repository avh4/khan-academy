from google.appengine.api import memcache
import util
import request_cache
import logging
class UserNotifier:
    # Only show up to 2 badge notifications at a time, rest
    # will be visible from main badges page.
    NOTIFICATION_LIMIT = 2
    
    @staticmethod
    def key_for_user(user):
        return "notifications_for_%s" % user.email()

    @staticmethod
    def push_login_for_user(user, user_alert):
        if user is None or user_alert is None:
            return

        notifications = memcache.get(UserNotifier.key_for_user(user)) or {"badges":[],"login":[]}
        notifications["login"] = [user_alert]

        memcache.set(UserNotifier.key_for_user(user), notifications)
    
    
    @staticmethod
    def push_badge_for_user(user, user_badge):
        if user is None or user_badge is None:
            return

        notifications = memcache.get(UserNotifier.key_for_user(user)) or {"badges":[],"login":[]}
        
        if notifications["badges"] is None:
            notifications["badges"] = []

        if len(notifications["badges"]) < UserNotifier.NOTIFICATION_LIMIT:
            notifications["badges"].append(user_badge)
            memcache.set(UserNotifier.key_for_user(user), notifications)
    
    @staticmethod
    @request_cache.cache()
    def pop_for_current_user():
        return UserNotifier.pop_for_user(util.get_current_user())

    @staticmethod
    def pop_for_user(user):
        if not user:
            return []
        notifications = memcache.get(UserNotifier.key_for_user(user)) or {"badges":[],"login":[]}
        user_badges = notifications["badges"] or []
        user_login = notifications["login"] or []
        
        if len(user_badges) > 0:
            notifications["badges"] = []
            memcache.set(UserNotifier.key_for_user(user), notifications)
            

        return user_badges,user_login
        
    @staticmethod
    def clear_login():
        notificationstemp = UserNotifier.pop_for_current_user()
        notifications = {"badges":[],"login":[]}
        notifications["login"] = []
        notifications["badges"] = notificationstemp[0]
        memcache.set(UserNotifier.key_for_user(util.get_current_user()), notifications)

        
        