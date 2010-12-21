from badges import Badge, BadgeContextType, BadgeCategory
from exercise_badges import ExerciseBadge

# All badges awarded for completing a streak of certain length inherit from StreakBadge
class StreakBadge(ExerciseBadge):

    def is_satisfied_by(self, *args, **kwargs):
        user_exercise = kwargs.get("user_exercise", None)
        if user_exercise is None:
            return False

        return user_exercise.longest_streak >= self.streak_required

    def extended_description(self):
        return "Correctly answer %s problems in a row in a single exercise" % str(self.streak_required)

class NiceStreakBadge(StreakBadge):

    def __init__(self):
        self.streak_required = 15
        self.description = "Nice Streak"
        self.badge_category = BadgeCategory.BRONZE
        self.points = 100
        StreakBadge.__init__(self)

class GreatStreakBadge(StreakBadge):
    def __init__(self):
        self.streak_required = 20
        self.description = "Great Streak"
        self.badge_category = BadgeCategory.BRONZE
        self.points = 1000
        StreakBadge.__init__(self)

class AwesomeStreakBadge(StreakBadge):
    def __init__(self):
        self.streak_required = 30
        self.description = "Awesome Streak"
        self.badge_category = BadgeCategory.SILVER
        self.points = 2000
        StreakBadge.__init__(self)

class RidiculousStreakBadge(StreakBadge):
    def __init__(self):
        self.streak_required = 50
        self.description = "Ridiculous Streak"
        self.badge_category = BadgeCategory.GOLD
        self.points = 5000
        StreakBadge.__init__(self)

class LudicrousStreakBadge(StreakBadge):
    def __init__(self):
        self.streak_required = 75
        self.description = "Ludicrous Streak"
        self.badge_category = BadgeCategory.PLATINUM
        self.points = 10000
        StreakBadge.__init__(self)
