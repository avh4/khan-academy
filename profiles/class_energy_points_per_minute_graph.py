from google.appengine.api import users

from django.utils import simplejson

import models
import util

def class_energy_points_per_minute_update(user_data, group):
    points = 0
    if user_data or group:
        if group:
            students_data = group.get_students_data()
        else:
            students_data = user_data.get_students_data()
        for student_data in students_data:
            points += student_data.points
    return simplejson.dumps({"points": points})

def class_energy_points_per_minute_graph_context(user_data, group):
    if not user_data:
        return {}
    user = user_data.user
    
    group_id = None
    if group:
        group_id = str(group.key())
        
    return { 'user_coach': user, 'coach_email': user.email(), 'group_id': group_id }
