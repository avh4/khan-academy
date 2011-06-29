from google.appengine.api import users

from django.utils import simplejson

import models
import util

def class_energy_points_per_minute_update(user_data, student_list):
    points = 0
    if user_data or student_list:
        if student_list:
            students_data = student_list.get_students_data()
        else:
            students_data = user_data.get_students_data()
        for student_data in students_data:
            points += student_data.points
    return simplejson.dumps({"points": points})

def class_energy_points_per_minute_graph_context(user_data, student_list):
    if not user_data:
        return {}
    user = user_data.user
    
    list_id = None
    if student_list:
        list_id = str(student_list.key())
        
    return { 'user_coach': user, 'coach_email': user.email(), 'list_id': list_id }
