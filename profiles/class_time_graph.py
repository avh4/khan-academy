import datetime
import time
import logging

from google.appengine.api import users
from django.template.defaultfilters import pluralize

import models
import classtime
import util

def class_time_graph_context(user_data, dt_utc, tz_offset):

    if not user_data:
        return {}

    user = user_data.user

    students_data = user_data.get_students_data()
    student_emails = map(lambda user_data_student: user_data_student.user.email(), students_data)

    classtime_table = None
    classtime_analyzer = classtime.ClassTimeAnalyzer(tz_offset)
    graph_data = []

    if classtime_analyzer.timezone_offset != -1:
        # If no timezone offset is specified, don't bother grabbing all the data
        # because we'll be redirecting back to here w/ timezone information.
        classtime_table = classtime_analyzer.get_classtime_table(student_emails, dt_utc)

    for user_data_student in students_data:

        short_name = util.get_nickname_for(user_data_student.display_user)
        if len(short_name) > 18:
            short_name = short_name[0:18] + "..."

        total_student_minutes = 0
        if classtime_table is not None:
            total_student_minutes = classtime_table.get_student_total(user_data_student.user.email())

        graph_data.append({
            "name": short_name,
            "total_minutes": "~%.0f" % total_student_minutes
            })

    return {
            "classtime_table": classtime_table,
            "coach_email": user.email(),
            "width": (60 * len(graph_data)) + 120,
            "graph_data": graph_data,
            "is_graph_empty": len(classtime_table.rows) <= 0
        }

