import logging
import os
import datetime
import urllib

from django.utils import simplejson as json
from google.appengine.ext.webapp import template
from google.appengine.api import users

from app import App
import app
import util
import request_handler

import coaches
from models import UserExercise, Exercise, UserData, ProblemLog, UserVideo, Playlist, VideoPlaylist, Video, ExerciseVideo      
from discussion import qa
from topics_list import all_topics_list



class Export(request_handler.RequestHandler):

    def datetime_to_str(self, datetime):
        try:
            str = datetime.strftime('%Y-%m-%d %H:%M:%S')
        except:
            str = ""
        return str
        
    def get(self):  
        user = util.get_current_user()
        student = user
        if user:
            student_email = self.request.get('student_email')
            if student_email and student_email != user.email():
                #logging.info("user is a coach trying to look at data for student")
                student = users.User(email=student_email)
                user_data = UserData.get_or_insert_for(student)
                if users.is_current_user_admin():
                    pass # allow admin to export anyone's data
                elif user.email() not in user_data.coaches and user.email().lower() not in user_data.coaches:
                    raise Exception('Student '+ student_email + ' does not have you as their coach')
            else:
                #logging.info("user is a student looking at their own data")
                user_data = UserData.get_or_insert_for(user)  
                                                
            user_data_dict = {
                       'email': user_data.user.email(),
                       'moderator': user_data.moderator,
                       'joined': self.datetime_to_str(user_data.joined),     
                       'last_login': self.datetime_to_str(user_data.last_login),
                       'proficient_exercises': user_data.proficient_exercises,
                       'all_proficient_exercises': user_data.all_proficient_exercises,
                       'suggested_exercises': user_data.suggested_exercises,
                       'assigned_exercises': user_data.assigned_exercises,
                       'need_to_reassess': user_data.need_to_reassess,
                       'points': user_data.points,
                       'coaches': user_data.coaches,
                       }
            
            user_exercises = []
            for ue in UserExercise.all().filter('user =', student):
                ue_dict = {'exercise': ue.exercise,
                           'streak': ue.streak,
                           'longest_streak': ue.longest_streak,
                           'first_done': self.datetime_to_str(ue.first_done),
                           'last_done': self.datetime_to_str(ue.last_done),
                           'total_done': ue.total_done,
                           'last_review': self.datetime_to_str(ue.last_review),
                           'review_interval_secs': ue.review_interval_secs,                       
                           'proficient_date': self.datetime_to_str(ue.proficient_date),                       
                }
                user_exercises.append(ue_dict)            
    
            user_videos = []
            for uv in UserVideo.all().filter('user =', student):
                uv_dict = {'video': uv.video.youtube_id,
                           'seconds_watched': uv.seconds_watched,
                           'last_second_watched': uv.last_second_watched,
                           'last_watched': self.datetime_to_str(uv.last_watched),        
                }
                user_videos.append(uv_dict)  
                
            problems = []
            for problem in ProblemLog.all().filter('user =', student):
                problem_dict = {'exercise': problem.exercise,
                                'correct': problem.correct,
                                'time_done': self.datetime_to_str(problem.time_done),
                                'time_taken': problem.time_taken,
                                'problem_number': problem.problem_number,
                                'hint_used': problem.hint_used
                }        
                problems.append(problem_dict)    
            
            export_dict = {'UserData': user_data_dict,
                           'UserExercise': user_exercises,
                           'ProblemLog': problems,
                           'UserVideo': user_videos}
            self.response.out.write(json.dumps(export_dict, indent=4))
        else:
            self.redirect(util.create_login_url(self.request.uri))


class ImportUserData(request_handler.RequestHandler):

    def datetime_from_str(self, text): 
        try:
            return datetime.datetime.strptime(text, '%Y-%m-%d %H:%M:%S') 
        except:
            return None  
            
    def get_video(self, youtube_id):
        return Video.all().filter('youtube_id =', youtube_id).get()
        
    def post(self):  
        user = util.get_current_user()
        student = user        
        if not user:
            self.response.out.write("please login first")        
        elif App.is_dev_server:
            student_email = self.request.get('student_email')
            if student_email and student_email != user.email():
                #logging.info("user is a coach trying to look at data for student")
                student = users.User(email=student_email)
                user_data = UserData.get_or_insert_for(student)
                if users.is_current_user_admin():
                    pass # allow admin to import to anyone's account                
                elif user.email() not in user_data.coaches and user.email().lower() not in user_data.coaches:
                    raise Exception('Student '+ student_email + ' does not have you as their coach')
            else:
                #logging.info("user is a student looking at their own data")
                user_data = UserData.get_or_insert_for(user)  
                                
            file_contents = self.request.POST.get('userdata').file.read()
            import_dict = json.loads(file_contents)
            user_data_dict = import_dict['UserData']
            user_exercises = import_dict['UserExercise']
            problems_unsorted = import_dict['ProblemLog']
            user_videos = import_dict['UserVideo']
            
            user_data.moderator = user_data_dict['moderator']
            user_data.joined = self.datetime_from_str(user_data_dict['joined'])
            user_data.last_login = self.datetime_from_str(user_data_dict['last_login'])
            user_data.proficient_exercises = user_data_dict['proficient_exercises']
            user_data.all_proficient_exercises = user_data_dict['all_proficient_exercises']
            user_data.suggested_exercises = user_data_dict['suggested_exercises']
            user_data.assigned_exercises = user_data_dict['assigned_exercises']
            user_data.need_to_reassess = user_data_dict['need_to_reassess']
            user_data.points = user_data_dict['points']          
            user_data.coaches = user_data_dict['coaches']
            user_data.put()

            proficient_dates = {}    
            correct_in_a_row = {}
            for problem in ProblemLog.all().filter('user =', student):
                problem.delete()
            problems = sorted(problems_unsorted, key=lambda k: self.datetime_from_str(k['time_done']))
            
            for problem in problems:
                problem_log = ProblemLog()
                problem_log.user = student
                problem_log.exercise = problem['exercise']
                problem_log.time_done = self.datetime_from_str(problem['time_done'])
                problem_log.correct = problem['correct']
                if problem_log.correct:
                    if problem_log.exercise not in correct_in_a_row:
                        correct_in_a_row[problem_log.exercise] = 1                    
                    else:
                        correct_in_a_row[problem_log.exercise] += 1                    
                    if not problem_log.exercise in proficient_dates and correct_in_a_row[problem_log.exercise] == 10:
                        proficient_dates[problem_log.exercise] = problem_log.time_done
                        #for coach in user_data.coaches:                            
                        #    class_data = coaches.Class.get_or_insert(coach, coach=coach)     
                        #    class_data.compute_stats(user_data, problem_log.time_done.date())                                                  
                problem_log.time_taken = problem['time_taken']
                if problem.has_key('problem_number'):
                    problem_log.problem_number = problem['problem_number']
                if problem.has_key('hint_used'):                    
                    problem_log.hint_used = problem['hint_used']               
                problem_log.put()  
                
            for user_exercise in UserExercise.all().filter('user =', student):
                user_exercise.delete()
            for ue in user_exercises:
                user_exercise = UserExercise()
                user_exercise.key_name = ue['exercise']
                user_exercise.parent = user_data
                user_exercise.user = student
                user_exercise.exercise = ue['exercise']
                user_exercise.streak = ue['streak']
                user_exercise.longest_streak = ue['longest_streak']
                user_exercise.first_done = self.datetime_from_str(ue['first_done'])
                user_exercise.last_done = self.datetime_from_str(ue['last_done'])
                user_exercise.total_done = ue['total_done']
                last_review = self.datetime_from_str(ue['last_review'])
                if last_review:
                    user_exercise.last_review = last_review
                user_exercise.review_interval_secs = ue['review_interval_secs']
                if user_exercise.exercise in proficient_dates:
                    user_exercise.proficient_date = proficient_dates[user_exercise.exercise]   
                else:
                    user_exercise.proficient_date = self.datetime_from_str(ue['proficient_date'])
                user_exercise.put()

            for user_video in UserVideo.all().filter('user =', student):
                user_video.delete()
            for uv in user_videos:
                user_video = UserVideo()
                user_video.user = student
                user_video.video = self.get_video(uv["video"])
                if "last_second_watched" in uv:                  
                    user_video.last_second_watched = uv["last_second_watched"]
                user_video.seconds_watched = uv["seconds_watched"]
                user_video.last_watched = self.datetime_from_str(uv["last_watched"])  
                user_video.put()                                    
                
            self.redirect('/individualreport?student_email='+student.email())
        else:
            self.response.out.write("import is not supported on the live site")
               

class ViewImport(request_handler.RequestHandler):

    def get(self):  
        user = util.get_current_user()
        user_data = UserData.get_for_current_user()
        logout_url = users.create_logout_url(self.request.uri)
        template_values = qa.add_template_values({'App': App,
                                                  'points': user_data.points,
                                                  'username': user and user.nickname() or "",
                                                  'login_url': util.create_login_url(self.request.uri),
                                                  'student_email' : self.request.get('student_email'),
                                                  'logout_url': logout_url}, 
                                                  self.request)

        path = os.path.join(os.path.dirname(__file__), 'import.html')
        self.response.out.write(template.render(path, template_values)) 
        
        
class Playlists(request_handler.RequestHandler):

    def get(self): 
        playlists = []   
        for playlist_title in all_topics_list:            
            query = Playlist.all()
            query.filter('title =', playlist_title)
            playlist = query.get()
            playlist_dict = {'youtube_id':  playlist.youtube_id,
                             'youtube_url': playlist.url,
                             'title': playlist.title, 
                             'description': playlist.description,
                             'api_url': "http://www.khanacademy.org/api/playlistvideos?playlist=%s" % (urllib.quote_plus(playlist_title),)
                            } 
            playlists.append(playlist_dict) 
        self.response.out.write(json.dumps(playlists, indent=4))        
                             
        
class PlaylistVideos(request_handler.RequestHandler):

    def get(self): 
        playlist_title = self.request.get('playlist')
        query = Playlist.all()
        query.filter('title =', playlist_title)
        playlist = query.get()
        query = VideoPlaylist.all()
        query.filter('playlist =', playlist)
        query.filter('live_association = ', True)
        query.order('video_position')
        videos = []       
        for pv in query.fetch(500):
            v = pv.video
            video_dict = {'youtube_id':  v.youtube_id,
                          'youtube_url': v.url,
                          'title': v.title, 
                          'description': v.description,
                          'keywords': v.keywords,                         
                          'readable_id': v.readable_id,
                          'ka_url': "http://www.khanacademy.org/video/%s?playlist=%s" % (v.readable_id, urllib.quote_plus(playlist_title)),
                          'video_position': pv.video_position
                         }                         
            videos.append(video_dict)                        
        self.response.out.write(json.dumps(videos, indent=4))     
        

class VideosForExercise(request_handler.RequestHandler):

   def get(self):
       exid = self.request.get('exid')
       exercise = Exercise.all().filter('name =', exid).get()

       exercise_videos = []
       for exercise_video in ExerciseVideo.all().filter('exercise =', exercise):
            v = exercise_video.video
            video_dict = {'youtube_id':  v.youtube_id,
                          'youtube_url': v.url,
                          'title': v.title, 
                          'description': v.description,
                          'keywords': v.keywords,                         
                          'readable_id': v.readable_id,
                          'ka_url': "http://www.khanacademy.org/video/%s" % (v.readable_id,)
                         }         
            exercise_videos.append(video_dict)

       self.response.out.write(json.dumps(exercise_videos, indent=4))
       
        
