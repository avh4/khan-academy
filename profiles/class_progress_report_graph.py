from google.appengine.api import users

from django.template.defaultfilters import escape

import models
import util

def get_class_exercises(list_student_data):

    class_exercise_dict = {}

    for student_data in list_student_data:

        student = student_data.user
        student_email = student.email()

        class_exercise_dict[student_email] = {"student_data": student_data}

        user_exercises = models.UserExercise.get_for_user_use_cache(student)
        for user_exercise in user_exercises:
            if user_exercise.exercise not in class_exercise_dict[student_email]:
                class_exercise_dict[student_email][user_exercise.exercise] = user_exercise

    return class_exercise_dict

def class_progress_report_graph_context(user_data, studygroup):

    if not user_data:
        return {}
        
    if studygroup:
        user_data = studygroup

    list_student_data = user_data.get_students_data()
    student_emails = map(lambda student_data: student_data.user.email(), list_student_data)
    class_exercises = get_class_exercises(list_student_data)

    exercises_all = models.Exercise.get_all_use_cache()
    exercises_found = []

    for exercise in exercises_all:
        for student_email in student_emails:
            if class_exercises[student_email].has_key(exercise.name):
                exercises_found.append(exercise)
                break

    exercises_found_names = map(lambda exercise: exercise.name, exercises_found)
    exercise_data = {}

    for student_email in student_emails:   

        student_data = class_exercises[student_email]["student_data"]
        if not student_data:
            continue

        name = util.get_nickname_for(student_data.user)
        i = 0

        for exercise in exercises_found:

            exercise_name = exercise.name
            user_exercise = models.UserExercise()
            if class_exercises[student_email].has_key(exercise_name):
                user_exercise = class_exercises[student_email][exercise_name]

            if not exercise_data.has_key(exercise_name):
                exercise_data[exercise_name] = {}

            link = "/profile/graph/exerciseproblems?student_email="+student_email+"&exercise_name="+exercise_name

            status = ""
            hover = ""
            color = "transparent"

            if student_data.is_proficient_at(exercise_name):
                status = "Proficient"
                color = "proficient"

                if not student_data.is_explicitly_proficient_at(exercise_name):
                    status = "Proficient (due to proficiency in a more advanced module)"

            elif user_exercise.exercise is not None and models.UserExercise.is_struggling_with(user_exercise, exercise):
                status = "Struggling"
                color = "struggling"
            elif user_exercise.exercise is not None and user_exercise.total_done > 0:
                status = "Started"
                color = "started"

            exercise_display = models.Exercise.to_display_name(exercise_name)
            short_name = name
            if len(short_name) > 18:
                short_name = short_name[0:18] + "..."

            if len(status) > 0:
                hover = "<b>%s</b><br/><br/><b>%s</b><br/><em><nobr>Status: %s</nobr></em><br/><em>Streak: %s</em><br/><em>Problems attempted: %s</em>" % (escape(name), exercise_display, status, user_exercise.streak, user_exercise.total_done)

            exercise_data[exercise_name][student_email] = {
                    "name": name, 
                    "short_name": short_name, 
                    "exercise_display": exercise_display, 
                    "link": link, 
                    "hover": hover,
                    "color": color
                    }
            i += 1

    return { 
            'student_emails': student_emails,
            'exercise_names': exercises_found_names,
            'exercise_data': exercise_data,
        }
