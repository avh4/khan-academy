from django.template.defaultfilters import escape

import models
import util

def get_class_exercises(students):

    exercises = {}
    async_queries = []

    for s in students:
        exercises[s.email] = {"user_data_student": s}
        async_queries.append(models.UserExercise.get_for_user_data(s))

    results = util.async_queries(async_queries)

    for i, s in enumerate(students):

        user_exercises = results[i].get_result()
        for user_exercise in user_exercises:
            if user_exercise.exercise not in exercises[s.email]:
                exercises[s.email][user_exercise.exercise] = user_exercise

    return exercises

def class_progress_report_graph_context(user_data, student_list):

    if not user_data:
        return {}

    list_students = None
    if student_list:
        list_students = student_list.get_students_data()
    else:
        list_students = user_data.get_students_data()

    student_emails = [s.email for s in list_students]
    exercises = get_class_exercises(list_students)

    exercises_all = models.Exercise.get_all_use_cache()
    exercises_found = []

    for exercise in exercises_all:
        for email in student_emails:
            if exercises[email].has_key(exercise.name):
                exercises_found.append(exercise)
                break

    exercises_found_names = [e.name for e in exercises_found]
    exercise_data = {}

    for student_email in student_emails:

        student = exercises[student_email]["user_data_student"]
        if not student:
            continue

        name = student.nickname
        i = 0

        for exercise in exercises_found:

            exercise_name = exercise.name
            user_exercise = models.UserExercise()
            if exercises[student_email].has_key(exercise_name):
                user_exercise = exercises[student_email][exercise_name]

            if not exercise_data.has_key(exercise_name):
                exercise_data[exercise_name] = {}

            link = "/profile/graph/exerciseproblems?student_email=" + student.email + "&exercise_name="+exercise_name

            status = ""
            hover = ""
            color = "transparent"

            if student.is_proficient_at(exercise_name):
                status = "Proficient"
                color = "proficient"

                if not student.is_explicitly_proficient_at(exercise_name):
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
            'coach_email': user_data.email,
        }
