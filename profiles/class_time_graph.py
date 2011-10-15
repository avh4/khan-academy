import datetime
import time
import logging

from google.appengine.api import users

import models
import classtime
import util

def class_time_graph_context(user_data, dt_utc, tz_offset, student_list):

    if not user_data:
        return {}
    
    students_data = None
    if student_list:
        students_data = student_list.get_students_data()
    else:
        students_data = user_data.get_students_data()

    students_data = sorted(students_data, key=lambda student: student.nickname)
    classtime_table = None
    classtime_analyzer = classtime.ClassTimeAnalyzer(tz_offset)
    graph_data = []

    if classtime_analyzer.timezone_offset != -1:
        # If no timezone offset is specified, don't bother grabbing all the data
        # because we'll be redirecting back to here w/ timezone information.
        
        #TODO: remove commented out tests below and go with the version of get_classtime_table that is the fastest
        ''' 
        import time
        minOld=999999
        minNew=999999
        for i in range(1,2):
            start=time.time()
            classtime_table = classtime_analyzer.get_classtime_table_old(students_data, dt_utc)
            end=time.time()
            minOld=min(minOld, end-start)

            start=time.time()
            classtime_table = classtime_analyzer.get_classtime_table(students_data, dt_utc)
            end=time.time()
            minNew=min(minNew, end-start)
       
        logging.info("old="+ str(minOld))
        logging.info("new="+ str(minNew))
        '''
        import os
        import time
        
        if os.environ["QUERY_STRING"].find("&version=2")!=-1:
            start=time.time()
            classtime_table = classtime_analyzer.get_classtime_table(students_data, dt_utc)
            end=time.time()
            logging.info("new="+ str(end-start))
        elif os.environ["QUERY_STRING"].find("&version=3")!=-1:
            start=time.time()
            classtime_table = classtime_analyzer.get_classtime_table_by_coach(user_data, students_data, dt_utc)
            end=time.time()
            logging.info("new by coach="+ str(end-start))
        else:
            start=time.time()
            classtime_table = classtime_analyzer.get_classtime_table_old(students_data, dt_utc)
            end=time.time()
            logging.info("old="+ str(end-start))

    for user_data_student in students_data:

        short_name = user_data_student.nickname
        if len(short_name) > 18:
            short_name = short_name[0:18] + "..."

        total_student_minutes = 0
        if classtime_table is not None:
            total_student_minutes = classtime_table.get_student_total(user_data_student.email)

        graph_data.append({
            "name": short_name,
            "total_minutes": "~%.0f" % total_student_minutes
            })

    return {
            "classtime_table": classtime_table,
            "coach_email": user_data.email,
            "width": (60 * len(graph_data)) + 120,
            "graph_data": graph_data,
            "is_graph_empty": len(classtime_table.rows) <= 0,
            "user_data_students": students_data,
            "c_points": reduce(lambda a, b: a + b, map(lambda s: s.points, students_data), 0)
        }

