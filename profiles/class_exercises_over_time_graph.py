import logging

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

def class_exercises_over_time_graph_context(user_data, student_list):

    if not user_data:
        return {}

    end_date = None

    if student_list:
        students_data = student_list.get_students_data()
    else:
        students_data = user_data.get_students_data()

    dict_student_exercises = {}
    dict_exercises = {}

    for user_data_student in students_data:
        student_nickname = user_data_student.nickname
        dict_student_exercises[student_nickname] = { "nickname": student_nickname, "email": user_data_student.email, "exercises": [] }

        query = models.UserExercise.all()
        query.filter('user =', user_data_student.user)
        query.filter('proficient_date >', None)
        query.order('proficient_date')
        
        for user_exercise in query:
            joined = min(user_data.joined, user_exercise.proficient_date)
            days_until_proficient = (user_exercise.proficient_date - joined).days
            proficient_date = user_exercise.proficient_date.strftime('%m/%d/%Y')
            data = ExerciseData(student_nickname, user_exercise.exercise, user_exercise.exercise, days_until_proficient, proficient_date)
            dict_student_exercises[student_nickname]["exercises"].append(data)
            end_date = user_exercise.proficient_date

    return {
            "dict_student_exercises": dict_student_exercises,
            "user_data_students": students_data,
            "c_points": reduce(lambda a, b: a + b, map(lambda s: s.points, students_data), 0)
            }

