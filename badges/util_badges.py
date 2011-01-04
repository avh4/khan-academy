from google.appengine.api import users
from mapreduce import control
from mapreduce import operation as op
import sys

import util
import models
import badges
import models_badges
import last_action_cache

import streak_badges
import timed_problem_badges
import exercise_completion_badges
import exercise_completion_count_badges
import playlist_time_badges
import power_time_badges
import recovery_problem_badges
import unfinished_streak_problem_badges
import points_badges
import tenure_badges

import layer_cache
import request_handler

import logging

# Authoritative list of all badges
@layer_cache.cache_with_key("all_badges", layer=layer_cache.SINGLE_LAYER_IN_APP_MEMORY_CACHE_ONLY)
def all_badges():
    return [
        exercise_completion_count_badges.GettingStartedBadge(),
        exercise_completion_count_badges.MakingProgressBadge(),
        exercise_completion_count_badges.HardAtWorkBadge(),
        exercise_completion_count_badges.WorkHorseBadge(),
        exercise_completion_count_badges.MagellanBadge(),
        exercise_completion_count_badges.AtlasBadge(),

        points_badges.TenThousandaireBadge(),
        points_badges.HundredThousandaireBadge(),
        points_badges.FiveHundredThousandaireBadge(),
        points_badges.MillionaireBadge(),
        points_badges.TenMillionaireBadge(),

        streak_badges.NiceStreakBadge(),
        streak_badges.GreatStreakBadge(),
        streak_badges.AwesomeStreakBadge(),
        streak_badges.RidiculousStreakBadge(),
        streak_badges.LudicrousStreakBadge(),

        playlist_time_badges.NicePlaylistTimeBadge(),
        playlist_time_badges.GreatPlaylistTimeBadge(),
        playlist_time_badges.AwesomePlaylistTimeBadge(),
        playlist_time_badges.RidiculousPlaylistTimeBadge(),
        playlist_time_badges.LudicrousPlaylistTimeBadge(),

        timed_problem_badges.NiceTimedProblemBadge(),
        timed_problem_badges.GreatTimedProblemBadge(),
        timed_problem_badges.AwesomeTimedProblemBadge(),
        timed_problem_badges.RidiculousTimedProblemBadge(),
        timed_problem_badges.LudicrousTimedProblemBadge(),

        recovery_problem_badges.RecoveryBadge(),
        recovery_problem_badges.ResurrectionBadge(),

        unfinished_streak_problem_badges.SoCloseBadge(),
        unfinished_streak_problem_badges.KeepFightingBadge(),
        unfinished_streak_problem_badges.UndeterrableBadge(),

        power_time_badges.PowerFifteenMinutesBadge(),
        power_time_badges.PowerHourBadge(),
        power_time_badges.DoublePowerHourBadge(),

        exercise_completion_badges.LevelOneArithmeticianBadge(),
        exercise_completion_badges.LevelTwoArithmeticianBadge(),
        exercise_completion_badges.LevelThreeArithmeticianBadge(),
        exercise_completion_badges.TopLevelArithmeticianBadge(),

        exercise_completion_badges.LevelOneTrigonometricianBadge(),
        exercise_completion_badges.LevelTwoTrigonometricianBadge(),
        exercise_completion_badges.LevelThreeTrigonometricianBadge(),
        exercise_completion_badges.TopLevelTrigonometricianBadge(),

        exercise_completion_badges.LevelOnePrealgebraistBadge(),
        exercise_completion_badges.LevelTwoPrealgebraistBadge(),
        exercise_completion_badges.LevelThreePrealgebraistBadge(),
        exercise_completion_badges.TopLevelPrealgebraistBadge(),

        exercise_completion_badges.LevelOneAlgebraistBadge(),
        exercise_completion_badges.LevelTwoAlgebraistBadge(),
        exercise_completion_badges.LevelThreeAlgebraistBadge(),
        exercise_completion_badges.LevelFourAlgebraistBadge(),
        exercise_completion_badges.TopLevelAlgebraistBadge(),

        tenure_badges.YearOneBadge(),
        tenure_badges.YearTwoBadge(),
        tenure_badges.YearThreeBadge(),

    ]

@layer_cache.cache_with_key("all_badges_dict", layer=layer_cache.SINGLE_LAYER_IN_APP_MEMORY_CACHE_ONLY)
def all_badges_dict():
    dict_badges = {}
    for badge in all_badges():
        dict_badges[badge.name] = badge
    return dict_badges

def badges_with_context_type(badge_context_type):
    return filter(lambda badge: badge.badge_context_type == badge_context_type, all_badges())

def get_badge_counts(user_data):

    count_dict = badges.BadgeCategory.empty_count_dict()
    badges_dict = all_badges_dict()

    for badge_name_with_context in user_data.badges:
        badge_name = badges.Badge.remove_target_context(badge_name_with_context)
        badge = badges_dict.get(badge_name)
        if badge:
            count_dict[badge.badge_category] += 1

    return count_dict

class ViewBadges(request_handler.RequestHandler):

    def get(self):

        user = util.get_current_user()

        user_badges = []
        user_badges_dict = {}

        if user:
            user_badges = models_badges.UserBadge.get_for(user)
            badges_dict = all_badges_dict()
            user_badge_last = None
            for user_badge in user_badges:
                if user_badge_last and user_badge_last.badge_name == user_badge.badge_name:
                    user_badge_last.count += 1
                    if user_badge_last.count > 1:
                        user_badge_last.list_context_names_hidden.append(user_badge.target_context_name)
                    else:
                        user_badge_last.list_context_names.append(user_badge.target_context_name)
                else:
                    user_badge.badge = badges_dict.get(user_badge.badge_name)
                    user_badge.count = 1
                    user_badge.list_context_names = [user_badge.target_context_name]
                    user_badge.list_context_names_hidden = []
                    user_badge_last = user_badge
                    user_badges_dict[user_badge.badge_name] = True

        possible_badges = all_badges()
        for badge in possible_badges:
            badge.is_owned = user_badges_dict.has_key(badge.name)

        user_badges = sorted(filter(lambda user_badge: hasattr(user_badge, "badge"), user_badges), reverse=True, key=lambda user_badge:user_badge.date)
        possible_badges = sorted(possible_badges, key=lambda badge:badge.badge_category)

        user_badges_normal = filter(lambda user_badge: user_badge.badge.badge_category != badges.BadgeCategory.MASTER, user_badges)
        user_badges_master = filter(lambda user_badge: user_badge.badge.badge_category == badges.BadgeCategory.MASTER, user_badges)

        bronze_badges = sorted(filter(lambda badge:badge.badge_category == badges.BadgeCategory.BRONZE, possible_badges), key=lambda badge:badge.points or sys.maxint)
        silver_badges = sorted(filter(lambda badge:badge.badge_category == badges.BadgeCategory.SILVER, possible_badges), key=lambda badge:badge.points or sys.maxint)
        gold_badges = sorted(filter(lambda badge:badge.badge_category == badges.BadgeCategory.GOLD, possible_badges), key=lambda badge:badge.points or sys.maxint)
        platinum_badges = sorted(filter(lambda badge:badge.badge_category == badges.BadgeCategory.PLATINUM, possible_badges), key=lambda badge:badge.points or sys.maxint)
        diamond_badges = sorted(filter(lambda badge:badge.badge_category == badges.BadgeCategory.DIAMOND, possible_badges), key=lambda badge:badge.points or sys.maxint)
        master_badges = sorted(filter(lambda badge:badge.badge_category == badges.BadgeCategory.MASTER, possible_badges), key=lambda badge:badge.points or sys.maxint)
        
        template_values = {
                "user_badges_normal": user_badges_normal,
                "user_badges_master": user_badges_master,
                "badge_collections": [bronze_badges, silver_badges, gold_badges, platinum_badges, diamond_badges, master_badges],
                "show_badge_frequencies": self.request_bool("show_badge_frequencies", default=False)
                }

        self.render_template('viewbadges.html', template_values)

# /admin/startnewbadgemapreduce is called periodically by a cron job
class StartNewBadgeMapReduce(request_handler.RequestHandler):

    def get(self):

        # Admin-only restriction is handled by /admin/* URL pattern
        # so this can be called by a cron job.

        # Start a new Mapper task for calling badge_update_map
        mapreduce_id = control.start_map(
                name = "UpdateUserBadges",
                handler_spec = "badges.util_badges.badge_update_map",
                reader_spec = "mapreduce.input_readers.DatastoreInputReader",
                reader_parameters = {"entity_kind": "models.UserData"})

        self.response.out.write("OK: " + str(mapreduce_id))

# badge_update_map is called by a background MapReduce task.
# Each call updates the badges for a single user.
def badge_update_map(user_data):
    user = user_data.user

    if user is None:
        return

    action_cache = last_action_cache.LastActionCache.get_for_user(user)

    # Update all no-context badges
    awarded = update_with_no_context(user, user_data, action_cache=action_cache)

    # Update all exercise-context badges
    for user_exercise in models.UserExercise.get_for_user_use_cache(user):
        awarded = update_with_user_exercise(user, user_data, user_exercise, action_cache=action_cache) or awarded

    # Update all playlist-context badges
    for user_playlist in models.UserPlaylist.get_for_user(user):
        awarded = update_with_user_playlist(user, user_data, user_playlist, action_cache=action_cache) or awarded

    if awarded:
        yield op.db.Put(user_data)

# Award this user any earned no-context badges.
def update_with_no_context(user, user_data, action_cache = None):
    possible_badges = badges_with_context_type(badges.BadgeContextType.NONE)
    action_cache = action_cache or last_action_cache.LastActionCache.get_for_user(user)

    awarded = False
    for badge in possible_badges:
        if not badge.is_already_owned_by(user_data=user_data):
            if badge.is_satisfied_by(user_data=user_data, action_cache=action_cache):
                badge.award_to(user=user, user_data=user_data)
                awarded = True

    return awarded

# Award this user any earned Exercise-context badges for the provided UserExercise.
def update_with_user_exercise(user, user_data, user_exercise, include_other_badges = False, action_cache = None):
    possible_badges = badges_with_context_type(badges.BadgeContextType.EXERCISE)
    action_cache = action_cache or last_action_cache.LastActionCache.get_for_user(user)

    awarded = False
    for badge in possible_badges:
        # Pass in pre-retrieved user_exercise data so each badge check doesn't have to talk to the datastore
        if not badge.is_already_owned_by(user_data=user_data, user_exercise=user_exercise):
            if badge.is_satisfied_by(user_data=user_data, user_exercise=user_exercise, action_cache=action_cache):
                badge.award_to(user=user, user_data=user_data, user_exercise=user_exercise)
                awarded = True

    if include_other_badges:
        awarded = update_with_no_context(user, user_data, action_cache=action_cache) or awarded

    return awarded

# Award this user any earned Playlist-context badges for the provided UserPlaylist.
def update_with_user_playlist(user, user_data, user_playlist, include_other_badges = False, action_cache = None):
    possible_badges = badges_with_context_type(badges.BadgeContextType.PLAYLIST)
    action_cache = action_cache or last_action_cache.LastActionCache.get_for_user(user)
    
    awarded = False
    for badge in possible_badges:
        # Pass in pre-retrieved user_playlist data so each badge check doesn't have to talk to the datastore
        if not badge.is_already_owned_by(user_data=user_data, user_playlist=user_playlist):
            if badge.is_satisfied_by(user_data=user_data, user_playlist=user_playlist, action_cache=action_cache):
                badge.award_to(user=user, user_data=user_data, user_playlist=user_playlist)
                awarded = True

    if include_other_badges:
        awarded = update_with_no_context(user, user_data, action_cache=action_cache) or awarded

    return awarded

