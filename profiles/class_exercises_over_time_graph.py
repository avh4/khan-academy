from google.appengine.api import users

import models
import util

class ExerciseData:
        def __init__(self, nickname, name, exid, days_until_proficient, proficient_date):
            self.nickname = nickname
            self.name = name
            self.exid = exid
            self.days_until_proficient = days_until_proficient
            self.proficient_date = proficient_date

        def display_name(self):
            return models.Exercise.to_display_name(self.name)

def class_exercises_over_time_graph_context(user_data):

    if not user_data:
        return {}

    user = user_data.user
    end_date = None

    student_emails = user_data.get_students()
    dict_student_exercises = {}
    dict_exercises = {}

    for student_email in student_emails:
        student = users.User(student_email)
        student_nickname = util.get_nickname_for(student)
        dict_student_exercises[student_nickname] = { "nickname": student_nickname, "email": student.email(), "exercises": [] }

        query = models.UserExercise.all()
        query.filter('user =', student)
        query.filter('proficient_date >', None)
        query.order('proficient_date')

        for user_exercise in query:
            days_until_proficient = (user_exercise.proficient_date - user_data.joined).days
            proficient_date = user_exercise.proficient_date.strftime('%m/%d/%Y')
            data = ExerciseData(student_nickname, user_exercise.exercise, user_exercise.exercise, days_until_proficient, proficient_date)
            dict_student_exercises[student_nickname]["exercises"].append(data)
            end_date = user_exercise.proficient_date

    return { 'dict_student_exercises': dict_student_exercises }

