# import the webapp module
from google.appengine.ext import webapp
from Notifications import UserNotifier

register = webapp.template.create_template_register()

@register.inclusion_tag(("../phantom_users/notifications.html", "phantom_users/notifications.html"))
def login_notifications(continue_url):
    login_notifications = UserNotifier.pop_for_current_user_data()
    if len(login_notifications) > 1:
        login_notifications = login_notifications[1]


    if len(login_notifications) > 0:
        login_notifications = login_notifications[0]

    return {"login_notifications": login_notifications, "continue": continue_url}
