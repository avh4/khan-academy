import models
import datetime
import util
import logging
from badges import Badge, BadgeContextType, BadgeCategory

# All badges awarded for completing being a member of the Khan Academy for various periods of time
# from TenureBadge
class TenureBadge(Badge):

    def is_satisfied_by(self, *args, **kwargs):
        user_data = kwargs.get("user_data", None)
        action_cache = kwargs.get("action_cache", None)
        if user_data is None or action_cache is None:
            return False

        # Make sure they've been a member for at least X years
        if user_data.joined is None or util.seconds_since(user_data.joined) < self.seconds_required:
            return False

        # Make sure they've seen recent activity of any sort in the past 30 days
        c_problem_logs = len(action_cache.problem_logs)
        c_video_logs = len(action_cache.video_logs)

        if c_problem_logs > 0:
            problem_log = action_cache.get_problem_log(c_problem_logs - 1)
            if util.seconds_since(problem_log.time_done) < 60 * 60 * 24 * 30:
                return True

        if c_video_logs > 0:
            video_log = action_cache.get_video_log(c_video_logs - 1)
            if util.seconds_since(video_log.time_watched) < 60 * 60 * 24 * 30:
                return True

        return False

    def extended_description(self):
        return "Remain an active member of the Khan Academy for %s" % util.seconds_to_time_string(self.seconds_required)

class YearOneBadge(TenureBadge):
    def __init__(self):
        TenureBadge.__init__(self)
        self.seconds_required = 60 * 60 * 24 * 365
        self.description = "Yuri Gagarin" # First human in space
        self.badge_category = BadgeCategory.BRONZE
        self.points = 0

class YearTwoBadge(TenureBadge):
    def __init__(self):
        TenureBadge.__init__(self)
        self.seconds_required = 60 * 60 * 24 * 365 * 2
        self.description = "Valentina Tereshkova" # First woman in space
        self.badge_category = BadgeCategory.SILVER
        self.points = 0

class YearThreeBadge(TenureBadge):
    def __init__(self):
        TenureBadge.__init__(self)
        self.seconds_required = 60 * 60 * 24 * 365 * 3
        self.description = "John Glenn" # Oldest person to fly in space
        self.badge_category = BadgeCategory.GOLD
        self.points = 0

