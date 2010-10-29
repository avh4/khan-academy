import logging
import os
import datetime
import itertools
from collections import deque
from pprint import pformat

from google.appengine.ext.webapp import template
from google.appengine.api import users

from app import App
import app

from models import UserExercise, Exercise, UserData, ProblemLog, ExerciseGraph


class ViewCoaches(app.RequestHandler):

    def get(self):
        user = app.get_current_user()
        if user:
            user_data = UserData.get_or_insert_for(user)
            logout_url = users.create_logout_url(self.request.uri)

            template_values = {
                'App' : App,
                'username': user.nickname(),
                'logout_url': logout_url,
                'coaches': user_data.coaches
                }

            path = os.path.join(os.path.dirname(__file__), 'viewcoaches.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect(app.create_login_url(self.request.uri))
            
            
class RegisterCoach(app.RequestHandler):
    
    def post(self):
        user = app.get_current_user()
        if user is None:
            self.redirect(app.create_login_url(self.request.uri))
            return

        user_data = UserData.get_or_insert_for(user)
        coach_email = self.request.get('coach').lower()            
        user_data.coaches.append(coach_email)
        user_data.put()
        self.redirect("/coaches")
            

class UnregisterCoach(app.RequestHandler):

    def post(self):
        user = app.get_current_user()
        if user is None:
            self.redirect(app.create_login_url(self.request.uri))
            return
        user_data = UserData.get_or_insert_for(user)
        coach_email = self.request.get('coach')
        if coach_email:
            if coach_email in user_data.coaches:
                user_data.coaches.remove(coach_email)
                user_data.put()
            elif coach_email.lower() in user_data.coaches:
                user_data.coaches.remove(coach_email.lower())
                user_data.put()                
        self.redirect("/coaches") 


class ViewIndividualReport(app.RequestHandler):

    def get(self):
        user = app.get_current_user()
        student = user
        if user:
            student_email = self.request.get('student_email')
            if student_email:
                #logging.info("user is a coach trying to look at data for student")
                student = users.User(email=student_email)
                user_data = UserData.get_or_insert_for(student)
                if user.email() not in user_data.coaches and user.email().lower() not in user_data.coaches:
                    raise Exception('Student '+ student_email + ' does not have you as their coach')
            else:
                #logging.info("user is a student looking at their own report")
                user_data = UserData.get_or_insert_for(user)                                   
            logout_url = users.create_logout_url(self.request.uri)   

            ex_graph = ExerciseGraph(user_data, user=student)
            for exercise in ex_graph.exercises:
                exercise.display_name = exercise.name.replace('_', ' ').capitalize()            
            proficient_exercises = ex_graph.get_proficient_exercises()
            self.compute_report(student, proficient_exercises, dummy_values=True)
            suggested_exercises = ex_graph.get_suggested_exercises()
            self.compute_report(student, suggested_exercises)
            review_exercises = ex_graph.get_review_exercises(self.get_time())
            self.compute_report(student, review_exercises)
            
            name = app.get_nickname_for(student)
            if student.email() != name:
                name = name + " (%s)" % student.email()
                   
            template_values = {
                'App' : App,
                'username': user.nickname(),
                'logout_url': logout_url,
                'proficient_exercises': proficient_exercises,
                'suggested_exercises': suggested_exercises,
                'review_exercises': review_exercises,  
                'student': name,                
                'student_email': student_email,                  
                }

            path = os.path.join(os.path.dirname(__file__), 'viewindividualreport.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect(app.create_login_url(self.request.uri))

    def compute_report(self, user, exercises, dummy_values=False):
            for exercise in exercises:
                #logging.info(exercise.name)             
                if dummy_values:
                    exercise.percent_correct = "-"
                    exercise.percent_of_last_ten = "-"                    
                else:
                    total_correct = 0
                    correct_of_last_ten = 0
                    problems = ProblemLog.all().filter('user =', user).filter('exercise =', exercise.name).order("-time_done")
                    problem_num = 0
                    for problem in problems:
                        #logging.info("problem.time_done: " + str(problem.time_done) + " " + str(problem.correct))
                        if problem.correct:
                            total_correct += 1
                            if problem_num < 10:
                                correct_of_last_ten += 1
                        problem_num += 1
                    #logging.info("total_done: " + str(exercise.total_done))
                    #logging.info("total_correct: " + str(total_correct))
                    #logging.info("correct_of_last_ten: " + str(correct_of_last_ten))
                    if problem_num > 0:
                        exercise.percent_correct = "%.0f%%" % (100.0*total_correct/problem_num,)
                    else:
                        exercise.percent_correct = "0%"            
                    exercise.percent_of_last_ten = "%.0f%%" % (100.0*correct_of_last_ten/10,)
                
    def get_time(self):
        time_warp = int(self.request.get('time_warp') or '0')
        return datetime.datetime.now() + datetime.timedelta(days=time_warp)      
            

class ViewProgressChart(app.RequestHandler):

    def get(self):    
        class ExerciseData:
            def __init__(self, name, exid, days_until_proficient):
                self.name = name
                self.exid = exid
                self.days_until_proficient = days_until_proficient
                
        user = app.get_current_user()
        student = user
        if user:
            student_email = self.request.get('student_email')
            if student_email:
                #logging.info("user is a coach trying to look at data for student")
                student = users.User(email=student_email)
                user_data = UserData.get_or_insert_for(student)
                if user.email() not in user_data.coaches and user.email().lower() not in user_data.coaches:
                    raise Exception('Student '+ student_email + ' does not have you as their coach')
            else:
                #logging.info("user is a student looking at their own report")
                user_data = UserData.get_or_insert_for(user)                  
            logout_url = users.create_logout_url(self.request.uri)   

            user_exercises = []
            max_days = None
            #logging.info("user_data.joined: " + str(user_data.joined))
            for ue in UserExercise.all().filter('user =', user_data.user).filter('proficient_date >', None).order('proficient_date'):
                days_until_proficient = (ue.proficient_date - user_data.joined).days   
                #logging.info(ue.exercise + ": " + str(ue.proficient_date))
                #logging.info("delta: " + str(ue.proficient_date - user_data.joined))
                data = ExerciseData(ue.exercise.replace('_', ' ').capitalize(), ue.exercise, days_until_proficient)
                user_exercises.append(data)
                max_days = days_until_proficient
            
            name = app.get_nickname_for(student)
            if student.email() != name:
                name = name + " (%s)" % student.email()
                   
            template_values = {
                'App' : App,
                'username': user.nickname(),
                'logout_url': logout_url,  
                'student': name,                
                'student_email': student_email,   
                'user_exercises': user_exercises,
                'max_days': max_days,
                }

            path = os.path.join(os.path.dirname(__file__), 'viewprogresschart.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect(app.create_login_url(self.request.uri))  
            
            
class ViewStudents(app.RequestHandler):

    def get(self):
        user = app.get_current_user()
        if user:
            user_data = UserData.get_or_insert_for(user)
            logout_url = users.create_logout_url(self.request.uri)
            
            student_emails = user_data.get_students()
            students = []
            for student_email in student_emails:   
                student = users.User(email=student_email)
                student_data = UserData.get_or_insert_for(student)
                student_data.user.name = app.get_nickname_for(student_data.user) 
                if student_email != student_data.user.name:
                   student_data.user.name += " (%s)" % student_email                                       
                students.append(student_data.user)

            template_values = {
                'App' : App,
                'username': user.nickname(),
                'logout_url': logout_url,
                'students': students,
                'coach_id': user_data.user.email(),
                }

            path = os.path.join(os.path.dirname(__file__), 'viewstudents.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect(app.create_login_url(self.request.uri))
        
        
class ViewClassReport(app.RequestHandler):
        
    def get(self):
        class ReportCell:
            def __init__(self, data="", css_class="", link=""):
                self.data = data
                self.css_class = css_class
                self.link = link
            
        user = app.get_current_user()
        if user:
            logout_url = users.create_logout_url(self.request.uri)   
            user_data = UserData.get_or_insert_for(user)  
            students = user_data.get_students()
            exercises = self.get_class_exercises(students)
            table_headers = []            
            table_headers.append("Name")
            working_total_row = []
            help_total_row = []
            proficient_total_row = []
            for exercise in exercises:
                table_headers.append(exercise.replace('_', ' ').capitalize()) 
                working_total_row.append(0)
                help_total_row.append(0)
                proficient_total_row.append(0)                
            table_data = []
            for student_email in students:   
                row = []
                student = users.User(email=student_email)
                student_data = UserData.get_or_insert_for(student)
                name = app.get_nickname_for(student_data.user)
                if student_email != name:
                    name = name + " (%s)" % student_email
                row.append(ReportCell(data='<a href="/progresschart?student_email=%s">%s</a>' % (student_email, name) ))
                i = 0
                for exercise in exercises:
                    link = "/charts?student_email="+student_email+"&exercise_name="+exercise 
                    if student_data.is_proficient_at(exercise):
                        row.append(ReportCell(css_class="proficient", link=link))
                        proficient_total_row[i] += 1
                    elif student_data.is_suggested(exercise):
                        if student_data.is_struggling_with(exercise):
                            row.append(ReportCell(css_class="needs_help", link=link))
                            help_total_row[i] += 1
                        else:
                            row.append(ReportCell(css_class="working", link=link))
                            working_total_row[i] += 1
                    else:
                        row.append(ReportCell())
                    i += 1
                table_data.append(row) 
            row = [ReportCell("Total students working (but not proficient):")]
            for count in working_total_row:
                row.append(ReportCell(data=count, css_class="number"))
            table_data.append(row) 

            row = [ReportCell("Total students needing help:")]
            for count in help_total_row:
                row.append(ReportCell(data=count, css_class="number"))
            table_data.append(row) 
            
            row = [ReportCell("Total proficient students:")]
            for count in proficient_total_row:
                row.append(ReportCell(data=count, css_class="number"))
            table_data.append(row)                       
            
            template_values = {
                'App' : App,
                'username': user.nickname(),
                'logout_url': logout_url,
                'table_headers': table_headers,
                'table_data': table_data,
                'coach_id': user_data.user.email(),
                }
            path = os.path.join(os.path.dirname(__file__), 'viewclassreport.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect(app.create_login_url(self.request.uri))
        
    def get_class_exercises(self, students):
            exercise_dict = {}
            for student_email in students:           
                student = users.User(email=student_email)
                student_data = UserData.get_or_insert_for(student)
                user_exercises = UserExercise.get_for_user_use_cache(student)
                for user_exercise in user_exercises:
                    if user_exercise.exercise not in exercise_dict:
                        exercise_dict[user_exercise.exercise] = 1
            results = []
            exercises = Exercise.get_all_use_cache()            
            for exercise in exercises:
                if exercise.name in exercise_dict:
                    results.append(exercise.name)
            return results            


class ViewCharts(app.RequestHandler):

    def moving_average(self, iterable, n=3):
        # moving_average([40, 30, 50, 46, 39, 44]) --> 40.0 42.0 45.0 43.0
        # http://en.wikipedia.org/wiki/Moving_average
        it = iter(iterable)
        d = deque(itertools.islice(it, n-1))
        d.appendleft(0)
        s = sum(d)
        for elem in it:
            s += elem - d.popleft()
            d.append(elem)
            yield s / float(n)    
                
    def get(self):
        class Problem:
            def __init__(self, time_taken, moving_average, correct):
                self.time_taken = time_taken
                self.moving_average = moving_average
                if correct:
                    self.correct = 1
                else:
                    self.correct = 0
        user = app.get_current_user()
        student = user
        if user:
            student_email = self.request.get('student_email')
            if student_email:
                #logging.info("user is a coach trying to look at data for student")
                student = users.User(email=student_email)
                user_data = UserData.get_or_insert_for(student)
                if user.email() not in user_data.coaches and user.email().lower() not in user_data.coaches:
                    raise Exception('Student '+ student_email + ' does not have you as their coach')
            else:
                #logging.info("user is a student looking at their own report")
                user_data = UserData.get_or_insert_for(user)   

            name = app.get_nickname_for(user_data.user)
            if user_data.user.email() != name:
                name = name + " (%s)" % user_data.user.email()
                
            logout_url = users.create_logout_url(self.request.uri)
            exercise_name = self.request.get('exercise_name')
            if not exercise_name:
                exercise_name = "addition_1"
              
            userExercise = user_data.get_or_insert_exercise(exercise_name)
            needs_proficient_date = False
            if user_data.is_proficient_at(exercise_name) and not userExercise.proficient_date:
                needs_proficient_date = True                 
        
            problem_list = []
            max_time_taken = 0  
            y_axis_interval = 1
            seconds_ranges = []
            problems = ProblemLog.all().filter('user =', student).filter('exercise =', exercise_name).order("time_done")            
            num_problems = problems.count()                           
            correct_in_a_row = 0
            proficient_date = None
            if num_problems > 2:          
                time_taken_list = []
                for problem in problems:  
                    time_taken_list.append(problem.time_taken)
                    if problem.time_taken > max_time_taken:
                        max_time_taken = problem.time_taken
                    problem_list.append(Problem(problem.time_taken, problem.time_taken, problem.correct))
                    #logging.info(str(problem.time_taken) + " " + str(problem.correct))  
                                        
                    if needs_proficient_date:
                        if problem.correct:
                            correct_in_a_row += 1
                        else:
                            correct_in_a_row = 0
                        if correct_in_a_row == 10:
                            proficient_date = problem.time_done
                    
                if needs_proficient_date and proficient_date:                    
                    userExercise.proficient_date = proficient_date 
                    userExercise.put()                        
                    
                if max_time_taken > 120:
                    max_time_taken = 120
                y_axis_interval = max_time_taken/5
                if y_axis_interval == 0:
                    y_axis_interval = max_time_taken/5.0            
                #logging.info("time_taken_list: " + str(time_taken_list))                                   
                #logging.info("max_time_taken: " + str(max_time_taken))
                #logging.info("y_axis_interval: " + str(y_axis_interval))

                averages = []   
                for average in self.moving_average(time_taken_list):
                    averages.append(int(average))
                #logging.info("averages: " + str(averages))
                for i in range(len(problem_list)):
                    problem = problem_list[i]
                    if i > 1:
                        problem.moving_average = averages[i-2]
                    #logging.info(str(problem.time_taken) + " " + str(problem.moving_average) + " " + str(problem.correct))                            

                range_size = self.get_range_size(num_problems, time_taken_list)
                #logging.info("range_size: " + str(range_size))  
                seconds_ranges = self.get_seconds_ranges(range_size)
                for problem in problem_list:
                    self.place_problem(problem, seconds_ranges)
                for seconds_range in seconds_ranges:
                    seconds_range.get_range_string(range_size)
                    seconds_range.get_percentages(num_problems)
                    #logging.info("seconds_range: " + str(seconds_range))  

            template_values = {
                'App' : App,
                'username': user.nickname(),
                'logout_url': logout_url,
                'exercise_name': exercise_name.replace('_', ' ').capitalize(),
                'problems': problem_list,
                'num_problems': num_problems,
                'max_time_taken': max_time_taken,
                'y_axis_interval': y_axis_interval,
                'student': name,
                'seconds_ranges': seconds_ranges,
                }

            path = os.path.join(os.path.dirname(__file__), 'viewcharts.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect(app.create_login_url(self.request.uri))

    def get_range_size(self, num_problems, time_taken_list):
        range_size = 0
        pct_under_top_range = 0
        while pct_under_top_range < 0.8:
            range_size += 1
            #logging.info("range_size: " + str(range_size))
            #logging.info("range_size*10: " + str(range_size*10))
            num_under_top_range = 0
            for time_taken in time_taken_list:
                if time_taken < range_size*10:
                    num_under_top_range += 1
            #logging.info("num_under_top_range: " + str(num_under_top_range))
            pct_under_top_range = 1.0*num_under_top_range/num_problems
            #logging.info("pct_under_top_range: " + str(pct_under_top_range))
        return range_size
        
    def get_seconds_ranges(self, range_size):
        class SecondsRange:
            def __init__(self, lower_bound, upper_bound):
                self.lower_bound = lower_bound
                self.upper_bound = upper_bound
                self.num_correct = 0
                self.num_incorrect = 0
                self.pct_correct = 0
                self.pct_incorrect = 0
            def get_range_string(self, range_size):
                if self.upper_bound is None:
                    self.range_string = "%s+" % (self.lower_bound,)
                elif range_size == 1:
                    self.range_string = "%s" % (self.lower_bound,)                    
                else:
                    self.range_string = "%s-%s" % (self.lower_bound, self.upper_bound)
            def get_percentages(self, num_problems):
                self.pct_correct = 100.0*self.num_correct/num_problems
                self.pct_incorrect = 100.0*self.num_incorrect/num_problems                
            def __repr__(self):
                return self.range_string + " correct: " + str(self.pct_correct) + " incorrect: " + str(self.pct_incorrect)
                
        seconds_ranges = []
        for lower_bound in range(0, range_size*9, range_size): 
            seconds_ranges.append(SecondsRange(lower_bound, lower_bound+range_size-1))
        seconds_ranges.append(SecondsRange(range_size*9, None))
        return seconds_ranges

    def place_problem(self, problem, seconds_ranges):
        for seconds_range in seconds_ranges:
            if problem.time_taken >= seconds_range.lower_bound and \
                (seconds_range.upper_bound is None or problem.time_taken <= seconds_range.upper_bound):
                if problem.correct:
                    seconds_range.num_correct += 1
                else:
                    seconds_range.num_incorrect += 1    