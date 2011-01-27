import util
import logging

from models import UserExercise, Exercise, UserData

def exercise_progress_graph_context(user_data_student):

    if not user_data_student:
        return {}
    
    user = user_data_student.user

    exercise_data = {}
    
    exercises = Exercise.get_all_use_cache()
    user_exercises = UserExercise.get_for_user_use_cache(user)

    dict_user_exercises = {}
    for user_exercise in user_exercises:
        dict_user_exercises[user_exercise.exercise] = user_exercise

    for exercise in exercises:
        chart_link =""
        status = ""
        color = "transparent"
        exercise_display = Exercise.to_display_name(exercise.name)
        ex_link = "/exercises?exid="+exercise.name
        hover = "<b>%s</b><br/><em><nobr>Status: %s</nobr></em><br/><em>Streak: %s</em><br/><em>Problems attempted: %s</em>" % ( exercise_display, "Not Started", 0, 0)

        chart_link = "/profile/graph/exerciseproblems?student_email=%s&exercise_name=%s" % (user.email(), exercise.name) 
                
        if dict_user_exercises.has_key(exercise.name):
            # User has done this exercise
            user_exercise = dict_user_exercises[exercise.name]
            exercise_name = user_exercise.exercise

            if user_data_student.is_proficient_at(exercise_name):
                status = "Proficient"
                color = "proficient"
    
                if not user_data_student.is_explicitly_proficient_at(exercise_name):
                    status = "Proficient (due to proficiency in a more advanced module)"
    
            elif user_exercise.exercise is not None and UserExercise.is_struggling_with(user_exercise, user_exercise.get_exercise()):
                status = "Struggling"
                color = "struggling"
            elif user_exercise.exercise is not None and user_exercise.total_done > 0:
                status = "Started"
                color = "started"
    
            if len(status) > 0:
                hover = "<b>%s</b><br/><em><nobr>Status: %s</nobr></em><br/><em>Streak: %s</em><br/><em>Problems attempted: %s</em>" % ( exercise_display, status, user_exercise.streak, user_exercise.total_done)

        exercise_data[exercise.name] = {
                "short_name": exercise.short_name(),
                "chart_link": chart_link,
                "ex_link": ex_link, 
                "hover": hover,
                "color": color
                }
                
    return { 'exercises': exercises, 'exercise_data': exercise_data, }
