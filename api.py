import logging
import os
import datetime

from django.utils import simplejson as json
from google.appengine.ext.webapp import template
from google.appengine.api import users

from app import App
import app
import util
import request_handler

from models import UserExercise, Exercise, UserData, ProblemLog, UserVideo, Playlist, VideoPlaylist, Video
        
from discussion import qa


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
                if user.email() not in user_data.coaches and user.email().lower() not in user_data.coaches:
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
                           'percent_watched': uv.percent_watched,
                           'seconds_watched': uv.seconds_watched,
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
                if user.email() not in user_data.coaches and user.email().lower() not in user_data.coaches:
                    raise Exception('Student '+ student_email + ' does not have you as their coach')
            else:
                #logging.info("user is a student looking at their own data")
                user_data = UserData.get_or_insert_for(user)  
                                
            file_contents = self.request.POST.get('userdata').file.read()
            import_dict = json.loads(file_contents)
            user_data_dict = import_dict['UserData']
            user_exercises = import_dict['UserExercise']
            problems = import_dict['ProblemLog']
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
                user_exercise.proficient_date = self.datetime_from_str(ue['proficient_date'])
                user_exercise.put()

            for user_video in UserVideo.all().filter('user =', student):
                user_video.delete()
            for uv in user_videos:
                user_video = UserVideo()
                user_video.user = student
                user_video.video = self.get_video(uv["video"])
                user_video.percent_watched = uv["percent_watched"]
                user_video.seconds_watched = uv["seconds_watched"]
                user_video.last_watched = self.datetime_from_str(uv["last_watched"])  
                user_video.put()
                                
            for problem in ProblemLog.all().filter('user =', student):
                problem.delete()
            for problem in problems:
                problem_log = ProblemLog()
                problem_log.user = student
                problem_log.exercise = problem['exercise']
                problem_log.correct = problem['correct']
                problem_log.time_done = self.datetime_from_str(problem['time_done'])
                problem_log.time_taken = problem['time_taken']
                if problem.has_key('problem_number'):
                    problem_log.problem_number = problem['problem_number']
                if problem.has_key('hint_used'):                    
                    problem_log.hint_used = problem['hint_used']               
                problem_log.put()        
                
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
        self.response.out.write(json.dumps(util.all_topics_list, indent=4))
        

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
                          'url': v.url,
                          'title': v.title, 
                          'description': v.description,
                          #'playlists': v.playlists,
                          'keywords': v.keywords,                         
                          'readable_id': v.readable_id,
                         }                         
            videos.append(video_dict) 

        playlist_dict = {'youtube_id':  playlist.youtube_id,
                         'url': playlist.url,
                         'title': playlist.title, 
                         'description': playlist.description,
                         #'readable_id': playlist.readable_id,
                         'videos': videos,
                        }                         
        self.response.out.write(json.dumps(playlist_dict, indent=4))        
        