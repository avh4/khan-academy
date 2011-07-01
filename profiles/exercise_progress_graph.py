import util
import logging

from models import UserExercise, Exercise, UserData

def exercise_progress_graph_context(user_data_student):

    if not user_data_student:
        return {}
    
    exercise_data = {}
    
    exercises = Exercise.get_all_use_cache()
    user_exercises = UserExercise.get_for_user_data_use_cache(user_data)

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

        chart_link = "/profile/graph/exerciseproblems?student_email=%s&exercise_name=%s" % (user_data.display_email, exercise.name) 
                
        user_exercise = dict_user_exercises[exercise.name] if dict_user_exercises.has_key(exercise.name) else None

        if user_data_student.is_proficient_at(exercise.name):
            status = "Proficient"
            color = "proficient"
            if not user_data_student.is_explicitly_proficient_at(exercise.name):
                status = "Proficient (due to proficiency in a more advanced module)"

        elif user_exercise is not None and UserExercise.is_struggling_with(user_exercise, exercise):
            status = "Struggling"
            color = "struggling"
        elif user_exercise is not None and user_exercise.total_done > 0:
            status = "Started"
            color = "started"

        if len(status) > 0:
            hover = "<b>%s</b><br/><em><nobr>Status: %s</nobr></em><br/><em>Streak: %s</em><br/><em>Problems attempted: %s</em>" % (exercise_display, 
                        status, 
                        user_exercise.streak if user_exercise is not None else 0, 
                        user_exercise.total_done if user_exercise is not None else 0)

        exercise_data[exercise.name] = {
                "short_name": exercise.short_name(),
                "chart_link": chart_link,
                "ex_link": ex_link, 
                "hover": hover,
                "color": color
                }
                
    return { 'exercises': exercises, 'exercise_data': exercise_data, }
