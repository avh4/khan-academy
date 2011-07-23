# import the webapp module
from google.appengine.ext import webapp
from notifications import UserNotifier
from .badges import badges, util_badges

register = webapp.template.create_template_register()

@register.simple_tag
def login_notifications(continue_url, user_data):
    login_notifications = UserNotifier.pop_for_current_user_data()["login"]

    if len(login_notifications) > 0:
        login_notifications = login_notifications[0]

    return webapp.template.render("phantom_users/notifications.html", {
        "login_notifications": login_notifications,
        "continue": continue_url,
        "user_data": user_data
    })
    
@register.simple_tag
def badge_info(user_data):

    counts_dict = {}
    if user_data:
        counts_dict = util_badges.get_badge_counts(user_data)
    else:
        counts_dict = badges.BadgeCategory.empty_count_dict()

    sum_counts = 0
    for key in counts_dict:
        sum_counts += counts_dict[key]

    return webapp.template.render("phantom_users/badge_counts.html", {
            "sum": sum_counts,
            "bronze": counts_dict[badges.BadgeCategory.BRONZE],
            "silver": counts_dict[badges.BadgeCategory.SILVER],
            "gold": counts_dict[badges.BadgeCategory.GOLD],
            "platinum": counts_dict[badges.BadgeCategory.PLATINUM],
            "diamond": counts_dict[badges.BadgeCategory.DIAMOND],
            "master": counts_dict[badges.BadgeCategory.MASTER],
    })
    
@register.simple_tag
def point_info(user_data):
    if user_data:
        points = user_data.points
    else:
        points = 0
    return webapp.template.render("phantom_users/user_points.html", {
        "points": points
    })
