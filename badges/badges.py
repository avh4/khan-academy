from google.appengine.api import memcache

import util
import models_badges
import logging

# Badges can either be Exercise badges (can earn one for every Exercise),
# Playlist badges (one for every Playlist),
# or context-less which means they can only be earned once.
class BadgeContextType:
    NONE = 0
    EXERCISE = 1
    PLAYLIST = 2

class BadgeCategory:
    # Sorted by astronomical size...
    BRONZE = 0 # Meteorite, "Common"
    SILVER = 1 # Moon, "Uncommon"
    GOLD = 2 # Earth, "Rare"
    PLATINUM = 3 # Sun, "Epic"
    DIAMOND = 4 # Black Hole, "Legendary"
    MASTER = 5 # Summative/Academic Achievement

    @staticmethod
    def empty_count_dict():
        count_dict = {}
        count_dict[BadgeCategory.BRONZE] = 0
        count_dict[BadgeCategory.SILVER] = 0
        count_dict[BadgeCategory.GOLD] = 0
        count_dict[BadgeCategory.PLATINUM] = 0
        count_dict[BadgeCategory.DIAMOND] = 0
        count_dict[BadgeCategory.MASTER] = 0
        return count_dict

# Badge is the base class used by various badge subclasses (ExerciseBadge, PlaylistBadge, TimedProblemBadge, etc).
# 
# Each baseclass overrides sets up a couple key pieces of data (description, badge_category, points)
# and implements a couple key functions (is_satisfied_by, is_already_owned_by, award_to, extended_description).
#
# The most important rule to follow with badges is to *never talk to the datastore when checking is_satisfied_by or is_already_owned_by*.
# Many badge calculations need to run every time a user answers a question or watches part of a video, and a couple slow badges can slow down
# the whole system.
# These functions are highly optimized and should only ever use data that is already stored in UserData or is passed as optional keyword arguments
# that have already been calculated / retrieved.
class Badge:

    def __init__(self):
        # Initialized by subclasses:
        #   self.description,
        #   self.badge_category,
        #   self.points

        # Keep .name constant even if description changes.
        # This way we only remove existing badges from people if the class name changes.
        self.name = self.__class__.__name__.lower()
        self.badge_context_type = BadgeContextType.NONE

        # Replace the badge's description with question marks
        # on the "all badges" page if the badge hasn't been achieved yet
        self.is_teaser_if_unknown = False

        # Hide the badge from all badge lists if it hasn't been achieved yet
        self.is_hidden_if_unknown = False
        
    @staticmethod
    def add_target_context_name(name, target_context_name):
        return "%s[%s]" % (name, target_context_name)

    @staticmethod
    def remove_target_context(name_with_context):
        ix = name_with_context.rfind("[")
        if ix >= 0:
            return name_with_context[:ix]
        else:
            return name_with_context

    def category_description(self):
        if self.badge_category == BadgeCategory.BRONZE:
            return "Meteorite badges are common and easy to earn when just getting started."
        elif self.badge_category == BadgeCategory.SILVER:
            return "Moon badges are uncommon and represent an investment in learning."
        elif self.badge_category == BadgeCategory.GOLD:
            return "Earth badges are rare. They require a significant amount of learning."
        elif self.badge_category == BadgeCategory.PLATINUM:
            return "Sun badges are epic. Earning them is a true challenge, and they require impressive dedication."
        elif self.badge_category == BadgeCategory.DIAMOND:
            return "Black Hole badges are legendary and unknown. They are the most unique Khan Academy awards."
        elif self.badge_category == BadgeCategory.MASTER:
            return "Challenge Patches are special awards for completing challenge exercises."
        return ""

    def icon_src(self):
        src = "/images/badges/half-moon-small.png"

        if self.badge_category == BadgeCategory.BRONZE:
            src = "/images/badges/meteorite-small.png"
        elif self.badge_category == BadgeCategory.SILVER:
            src = "/images/badges/moon-small.png"
        elif self.badge_category == BadgeCategory.GOLD:
            src = "/images/badges/earth-small.png"
        elif self.badge_category == BadgeCategory.PLATINUM:
            src = "/images/badges/sun-small.png"
        elif self.badge_category == BadgeCategory.DIAMOND:
            src = "/images/badges/eclipse-small.png"
        elif self.badge_category == BadgeCategory.MASTER:
            src = "/images/badges/master-challenge-blue.png"

        return util.static_url(src)

    def chart_icon_src(self):

        src = "/images/badges/meteorite-small-chart.png"

        if self.badge_category == BadgeCategory.BRONZE:
            src = "/images/badges/meteorite-small-chart.png"
        elif self.badge_category == BadgeCategory.SILVER:
            src = "/images/badges/moon-small-chart.png"
        elif self.badge_category == BadgeCategory.GOLD:
            src = "/images/badges/earth-small-chart.png"
        elif self.badge_category == BadgeCategory.PLATINUM:
            src = "/images/badges/sun-small-chart.png"
        elif self.badge_category == BadgeCategory.DIAMOND:
            src = "/images/badges/eclipse-small-chart.png"
        elif self.badge_category == BadgeCategory.MASTER:
            src = "/images/badges/master-challenge-blue-chart.png"

        return util.static_url(src)

    def type_label(self):
        if self.badge_category == BadgeCategory.BRONZE:
            return "Meteorite (Common)"
        elif self.badge_category == BadgeCategory.SILVER:
            return "Moon (Uncommon)"
        elif self.badge_category == BadgeCategory.GOLD:
            return "Earth (Rare)"
        elif self.badge_category == BadgeCategory.PLATINUM:
            return "Sun (Epic)"
        elif self.badge_category == BadgeCategory.DIAMOND:
            return "Black Hole (Legendary)"
        elif self.badge_category == BadgeCategory.MASTER:
            return "Challenge Patches (Challenge Completion)"
        return "Common"

    def name_with_target_context(self, target_context_name):
        if target_context_name is None:
            return self.name
        else:
            return Badge.add_target_context_name(self.name, target_context_name)

    # Overridden by individual badge implementations
    def extended_description(self):
        return ""

    # Overridden by individual badge implementations which each grab various parameters from args and kwargs.
    # *args and **kwargs should contain all the data necessary for is_satisfied_by's logic, and implementations of is_satisfied_by 
    # should never talk to the datastore or memcache, etc.
    def is_satisfied_by(self, *args, **kwargs):
        return False

    # Overridden by individual badge implementations which each grab various parameters from args and kwargs
    # *args and **kwargs should contain all the data necessary for is_already_owned_by's logic, and implementations of is_already_owned_by
    # should never talk to the datastore or memcache, etc.
    def is_already_owned_by(self, user_data, *args, **kwargs):
        return self.name in user_data.badges

    # Calculates target_context and target_context_name from data passed in and calls complete_award_to appropriately.
    #
    # Overridden by individual badge implementations which each grab various parameters from args and kwargs
    # It's ok for award_to to talk to the datastore, because it is run relatively infrequently.
    def award_to(self, user, user_data, *args, **kwargs):
        self.complete_award_to(user, user_data)

    # Awards badge to user within given context
    def complete_award_to(self, user, user_data, target_context=None, target_context_name=None):
        name_with_context = self.name_with_target_context(target_context_name)
        key_name = user.email() + ":" + name_with_context

        if user_data.badges is None:
            user_data.badges = []

        user_data.badges.append(name_with_context)

        user_badge = models_badges.UserBadge.get_by_key_name(key_name)

        if user_badge is None:
            user_data.add_points(self.points)

            user_badge = models_badges.UserBadge(
                    key_name = key_name,
                    user = user,
                    badge_name = self.name,
                    target_context = target_context,
                    target_context_name = target_context_name,
                    points_earned = self.points)

            user_badge.put()

        UserBadgeNotifier.push_for_user(user, user_badge)

    def frequency(self):
        return models_badges.BadgeStat.count_by_badge_name(self.name)

class UserBadgeNotifier:

    # Only show up to 2 badge notifications at a time, rest
    # will be visible from main badges page.
    NOTIFICATION_LIMIT = 2

    @staticmethod
    def key_for_user(user):
        return "badge_notifications_for_%s" % user.email()

    @staticmethod
    def push_for_user(user, user_badge):
        if user is None or user_badge is None:
            return

        user_badges = memcache.get(UserBadgeNotifier.key_for_user(user))

        if user_badges is None:
            user_badges = []

        if len(user_badges) < UserBadgeNotifier.NOTIFICATION_LIMIT:
            user_badges.append(user_badge)
            memcache.set(UserBadgeNotifier.key_for_user(user), user_badges)

    @staticmethod
    def pop_for_current_user():
        return UserBadgeNotifier.pop_for_user(util.get_current_user())

    @staticmethod
    def pop_for_user(user):
        user_badges = memcache.get(UserBadgeNotifier.key_for_user(user)) or []

        if len(user_badges) > 0:
            memcache.delete(UserBadgeNotifier.key_for_user(user))

        return user_badges

