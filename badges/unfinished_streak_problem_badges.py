from badges import Badge, BadgeContextType, BadgeCategory
from exercise_badges import ExerciseBadge
import logging

# All badges awarded for just barely missing streaks even though most questions are 
# being answered correctly inherit from UnfinishedStreakProblemBadge
class UnfinishedStreakProblemBadge(ExerciseBadge):

    def is_satisfied_by(self, *args, **kwargs):
        user_data = kwargs.get("user_data", None)
        user_exercise = kwargs.get("user_exercise", None)
        action_cache = kwargs.get("action_cache", None)

        if user_data is None or user_exercise is None or action_cache is None:
            return False

        # Make sure they've done the required minimum of problems in this exercise
        if user_exercise.total_done < self.problems_required:
            return False

        # Make sure they haven't yet reached explicit proficiency
        if user_data.is_explicitly_proficient_at(user_exercise.exercise):
            return False

        c_logs = len(action_cache.problem_logs)

        # Make sure the last problem is from this exercise and that they got it wrong
        last_problem_log = action_cache.get_problem_log(c_logs - 1)
        if (last_problem_log.exercise != user_exercise.exercise or last_problem_log.correct):
            return False

        c_correct = 0
        c_total = 0
        c_logs_examined = min(50, c_logs)

        # Look through the last 50 problems. If they've done at least 10 in the exercise
        # and gotten at least 75% correct but haven't managed to put together a streak, give 'em the badge.
        for i in range(c_logs_examined):

            problem_log = action_cache.get_problem_log(c_logs - i - 1)

            if problem_log.exercise == user_exercise.exercise:
                c_total += 1
                if problem_log.correct:
                    c_correct += 1

        # Make sure they've done at least 10 problems in this exercise out of their last 50
        if c_total < 10:
            return False

        # Make sure they've gotten at least 75% of their recent answers correct
        if (float(c_correct) / float(c_total)) < 0.75:
            return False

        return True

    def extended_description(self):
        return "Answer more than %d problems mostly correctly in an exercise before becoming proficient" % self.problems_required

class SoCloseBadge(UnfinishedStreakProblemBadge):

    def __init__(self):
        self.problems_required = 30
        self.description = "You're So Close"
        self.badge_category = BadgeCategory.BRONZE
        self.points = 0
        UnfinishedStreakProblemBadge.__init__(self)

class KeepFightingBadge(UnfinishedStreakProblemBadge):

    def __init__(self):
        self.problems_required = 40
        self.description = "Keep Fighting"
        self.badge_category = BadgeCategory.SILVER
        self.points = 0
        UnfinishedStreakProblemBadge.__init__(self)

class UndeterrableBadge(UnfinishedStreakProblemBadge):

    def __init__(self):
        self.problems_required = 50
        self.description = "Undeterrable"
        self.badge_category = BadgeCategory.GOLD
        self.points = 0
        UnfinishedStreakProblemBadge.__init__(self)

