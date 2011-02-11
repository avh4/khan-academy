from google.appengine.api import users

from django.utils import simplejson

import models
import util

def class_energy_points_per_minute_update(user_data):
    points = 0
    if user_data:
        students_data = user_data.get_students_data()
        for student_data in students_data:
            points += student_data.points
    return simplejson.dumps({"points": points})

def class_energy_points_per_minute_graph_context(user_data):
    if not user_data:
        return {}
    user = user_data.user
    return { 'user_coach': user, 'coach_email': user.email() }
