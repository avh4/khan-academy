import math
import consts

def ExercisePointCalculator(exercise, user_exercise, suggested, proficient):

    points = 0
    
    required_streak = exercise.required_streak()
    degrade_threshold = required_streak + consts.DEGRADING_EXERCISES_AFTER_STREAK

    if user_exercise.longest_streak <= required_streak:
        # Have never hit a streak, higher base than normal
        points = consts.INCOMPLETE_EXERCISE_POINTS_BASE
    elif user_exercise.longest_streak < degrade_threshold:
        # Significantly past hitting a streak, start to degrade points
        points = degrade_threshold - user_exercise.longest_streak

    if (points < consts.EXERCISE_POINTS_BASE):
        # Never award less than a few points
        points = consts.EXERCISE_POINTS_BASE
    
    if exercise.summative:
        # Slightly higher rewards for summative exercises
        points = points * consts.SUMMATIVE_EXERCISE_MULTIPLIER

    if suggested:
        # Higher awards for suggested
        points = points * consts.SUGGESTED_EXERCISE_MULTIPLIER

    if not proficient:
        # Higher awards for not being currently proficient
        points = points * consts.INCOMPLETE_EXERCISE_MULTIPLIER

    if not exercise.summative and user_exercise.total_done >= consts.LIMIT_EXERCISES_NON_SUMMATIVE:
        # Non-summative exercises can be gamed by getting 9 correct, then 1 wrong. Put an upper limit
        # on the number of problems that continue to award useful points for non-summative.
        points = consts.EXERCISE_POINTS_BASE

    return int(math.ceil(points))

def VideoPointCalculator(user_video):
    if user_video.duration is None or user_video.duration <= 0:
        return 0
    
    seconds_credit = min(user_video.seconds_watched, user_video.duration)

    credit_multiplier = float(seconds_credit) / float(user_video.duration)
    if credit_multiplier >= consts.REQUIRED_PERCENTAGE_FOR_FULL_VIDEO_POINTS:
        credit_multiplier = 1.0

    points = consts.VIDEO_POINTS_BASE * credit_multiplier

    return int(math.ceil(points))
