import cgi
import os
import datetime
import time
import random
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
import gdata.youtube
import gdata.youtube.service
import gdata.alt.appengine
import qbrary





class UserExercise(db.Model):
	user = db.UserProperty()
	exercise = db.StringProperty()
	streak = db.IntegerProperty()
	longest_streak = db.IntegerProperty()
	first_done = db.DateTimeProperty(auto_now_add=True)
	last_done = db.DateTimeProperty()
	total_done = db.IntegerProperty()	
	

class Exercise(db.Model):
	name = db.StringProperty()
	prerequisites = db.StringListProperty()
	covers = db.StringListProperty()
	v_position = db.IntegerProperty()
	h_position = db.IntegerProperty()
	
class UserData(db.Model):
	user = db.UserProperty()
	joined = db.DateTimeProperty(auto_now_add=True)
	last_login = db.DateTimeProperty()
	proficient_exercises = db.StringListProperty()
	suggested_exercises = db.StringListProperty()
	assigned_exercises = db.StringListProperty()
	need_to_reassess = db.BooleanProperty()
	points = db.IntegerProperty()

class Video(db.Model):
	youtube_id = db.StringProperty()
	url = db.StringProperty()
	title = db.StringProperty()
	description = db.TextProperty()
	playlists = db.StringListProperty()
	keywords = db.StringProperty()


class Playlist(db.Model):
	youtube_id = db.StringProperty()
	url = db.StringProperty()
	title = db.StringProperty()
	description = db.TextProperty()
	
class ProblemLog(db.Model):
	user = db.UserProperty()
	exercise = db.StringProperty()
	correct = db.BooleanProperty()
	time_done = db.DateTimeProperty()
	time_taken = db.IntegerProperty()

#Represents a matching between a playlist and a video
#Allows us to keep track of which videos are in a playlist and 
#which playlists a video belongs to (not 1-to-1 mapping)
class VideoPlaylist(db.Model):
	playlist = db.ReferenceProperty(Playlist)
	video = db.ReferenceProperty(Video)
	video_position = db.IntegerProperty()
	
#Matching between videos and exercises
class ExerciseVideo(db.Model):
	video = db.ReferenceProperty(Video)
	exercise = db.ReferenceProperty(Exercise)

#Matching between playlists and exercises
class ExercisePlaylist(db.Model):
	exercise = db.ReferenceProperty(Exercise)
	playlist = db.ReferenceProperty(Playlist)


def PointCalculator(streak, suggested, proficient):
	points = 5+max(streak,10)
	if suggested:
		points = points*3
	if not proficient:
		points = points*5
	return points

class VideoDataTest(webapp.RequestHandler):
	def get(self):
		self.response.out.write('<html>')
		videos = Video.all()
		for video in videos:
			self.response.out.write('<P>Title: '+video.title)
			

class DataStoreTest(webapp.RequestHandler):
	def get(self):
		self.response.out.write('<html>')
		user = users.get_current_user()
		if user:
			problems_done = ProblemLog.all()
			for problem in problems_done:
				self.response.out.write("<P>"+problem.user.nickname()+" "+problem.exercise+" done:"+str(problem.time_done)+" taken:"+str(problem.time_taken)+" correct:"+str(problem.correct))


#Setting this up to make sure the old Video-Playlist associations are flushed before the bulk upload from the local datastore (with the new associations)
class DeleteVideoPlaylists(webapp.RequestHandler):
	def get(self):
		query = VideoPlaylist.all()
		all_video_playlists = query.fetch(100000)
		for video_playlist in all_video_playlists:
			video_playlist.delete()
		


class UpdateVideoData(webapp.RequestHandler):
	def get(self):
		self.response.out.write('<html>')
		yt_service = gdata.youtube.service.YouTubeService()
		playlist_feed = yt_service.GetYouTubePlaylistFeed(uri='http://gdata.youtube.com/feeds/api/users/khanacademy/playlists?start-index=1&max-results=50')
		
		#The next two blocks delete all the Videos and VideoPlaylists so that we don't get remnant videos or associations 
		
		query = VideoPlaylist.all()
		all_video_playlists = query.fetch(100000)
		db.delete(all_video_playlists)

		query = Video.all()
		all_videos = query.fetch(100000)
		db.delete(all_videos)
			
		for playlist in playlist_feed.entry:
			self.response.out.write('<p>Playlist  '+playlist.id.text)
			playlist_id = playlist.id.text.replace('http://gdata.youtube.com/feeds/api/users/khanacademy/playlists/','')
			playlist_uri = playlist.id.text.replace('users/khanacademy/','') 
			query = Playlist.all()
			query.filter("youtube_id =", playlist_id)
			playlist_data = query.get()
			if not playlist_data:
				playlist_data = Playlist(youtube_id=playlist_id)
			playlist_data.url = playlist_uri
			playlist_data.title = playlist.title.text
			playlist_data.description = playlist.description.text
			playlist_data.put()
			
			for i in range(0,4):
				start_index = i*50+1
				video_feed = yt_service.GetYouTubePlaylistVideoFeed(uri=playlist_uri+"?start-index="+str(start_index)+"&max-results=50")
				for video in video_feed.entry:
					
					video_id = video.media.player.url.replace('http://www.youtube.com/watch?v=','')
					video_id = video_id.replace('&feature=youtube_gdata','')
					query = Video.all()
					query.filter("youtube_id =", video_id.decode("windows-1252"))
					video_data =query.get()
					if not video_data:
						video_data = Video(youtube_id=video_id.decode("windows-1252"))
						video_data.playlists = []
					video_data.title = video.media.title.text.decode("windows-1252")
					video_data.url = video.media.player.url.decode("windows-1252")
					if video.media.description.text is not None:
						video_data.description = video.media.description.text.decode("windows-1252")
					else:
						video_data.decription = " "
					
					if playlist.title.text not in video_data.playlists:
						video_data.playlists.append(playlist.title.text.decode("windows-1252"))
					video_data.keywords = video.media.keywords.text.decode("windows-1252")
					video_data.put()
					query = VideoPlaylist.all()
					query.filter("playlist =", playlist_data.key())
					query.filter("video =", video_data.key())
					playlist_video = query.get()
					if not playlist_video:
						playlist_video = VideoPlaylist(playlist=playlist_data.key(),video=video_data.key())
					self.response.out.write('<p>Playlist  '+playlist_video.playlist.title)
					playlist_video.video_position = int(video.position.text)
					playlist_video.put()
					
					
class UpdatePlaylistVideoData(webapp.RequestHandler):
	def get(self):
		self.response.out.write('<html>')
		yt_service = gdata.youtube.service.YouTubeService()
		playlist_feed = yt_service.GetYouTubePlaylistFeed(uri='http://gdata.youtube.com/feeds/api/users/khanacademy/playlists?start-index=1&max-results=50')
		playlist_number_string = self.request.get('playlist_number')  #only update this playlist--instead of the 34+ ones. Hacking this to avoid the timeout at the production server
		playlist_number = int(playlist_number_string)
		count = 0
		for playlist in playlist_feed.entry:
			count = count +1
			if count==playlist_number:
				self.response.out.write('<p>Playlist  '+playlist.id.text)
				playlist_id = playlist.id.text.replace('http://gdata.youtube.com/feeds/api/users/khanacademy/playlists/','')
				playlist_uri = playlist.id.text.replace('users/khanacademy/','') 
				query = Playlist.all()
				query.filter("youtube_id =", playlist_id)
				playlist_data = query.get()
				if not playlist_data:
					playlist_data = Playlist(youtube_id=playlist_id)
				playlist_data.url = playlist_uri
				playlist_data.title = playlist.title.text
				playlist_data.description = playlist.description.text
				playlist_data.put()
				
				for i in range(0,4):
					start_index = i*50+1
					video_feed = yt_service.GetYouTubePlaylistVideoFeed(uri=playlist_uri+"?start-index="+str(start_index)+"&max-results=50")
					for video in video_feed.entry:
						
						video_id = video.media.player.url.replace('http://www.youtube.com/watch?v=','')
						video_id = video_id.replace('&feature=youtube_gdata','')
						query = Video.all()
						query.filter("youtube_id =", video_id.decode("windows-1252"))
						video_data =query.get()
						if not video_data:
							video_data = Video(youtube_id=video_id.decode("windows-1252"))
							video_data.playlists = []
						video_data.title = video.media.title.text.decode("windows-1252")
						video_data.url = video.media.player.url.decode("windows-1252")
						video_data.description = video.media.description.text.decode("windows-1252")
						
						if playlist.title.text not in video_data.playlists:
							video_data.playlists.append(playlist.title.text.decode("windows-1252"))
						video_data.keywords = video.media.keywords.text.decode("windows-1252")
						video_data.put()
						query = VideoPlaylist.all()
						query.filter("playlist =", playlist_data.key())
						query.filter("video =", video_data.key())
						playlist_video = query.get()
						if not playlist_video:
							playlist_video = VideoPlaylist(playlist=playlist_data.key(),video=video_data.key())
						
						playlist_video.video_position = int(video.position.text)
						playlist_video.put()
				self.response.out.write('<p>Done Update  ')
			
					

class ViewExercise(webapp.RequestHandler):
    def get(self):
    	    user = users.get_current_user()
    	    if user:
    	    	    exid = self.request.get('exid')
    	    	    key = self.request.get('key')
    	    	    proficient = self.request.get('proficient')
    	    	    
    	    	    query = UserExercise.all()
    	    	    query.filter("user =", user)
    	    	    query.filter("exercise =", exid)
    	    	    userExercise = query.get()
    	    	    
    	    	    query = UserData.all()
		    query.filter("user =", user)
		    user_data = query.get()
    	    	    
    	    	    query = Exercise.all()
    	    	    query.filter("name =", exid)
    	    	    exercise = query.get()
    	    	    
    	    	    exercise_videos = None
    	    	    query = ExerciseVideo.all()
    	    	    query.filter("exercise =", exercise.key())
    	    	    exercise_videos = query.fetch(50)
    	    	    
    	    	    if not exid:
    	    	    	    exid = "addition_1"
    	    	    
    	    	    if not userExercise:
    	    	    	    userExercise = UserExercise(user=user,exercise=exid,streak=0,longest_streak=0,first_done=datetime.datetime.now(),last_done=datetime.datetime.now(),total_done=0)
    	    	    	    userExercise.put()
    	    	    
    	    	    logout_url = users.create_logout_url(self.request.uri)
    	    	    
    	    	    
    	    	    template_values = {
    	    	    	'username': user.nickname(),
    	    	    	'points': user_data.points,
    	    	    	'proficient': proficient,
    	    	    	'cookiename': user.nickname().replace('@','at'),
    	    	    	'key': userExercise.key(),
    	    	    	'exercise': exercise,
    	    	    	'exid': exid,
    	    	    	'start_time': time.time(),
    	    	    	'exercise_videos':exercise_videos,
    	    	    	'extitle': exid.replace('_', ' ').capitalize(),
    	    	    	'streakwidth': userExercise.streak*20,
    	    	    	'logout_url': logout_url,
    	    	    	'streak': userExercise.streak }
    	    	    	
    	    	    path = os.path.join(os.path.dirname(__file__), exid+'.html')
    	    	    self.response.out.write(template.render(path, template_values))
    	    	    
    	    else:
    	    	    self.redirect(users.create_login_url(self.request.uri))
    	    
    	    
    	    
    	    
class ViewVideo(webapp.RequestHandler):
    def get(self):
	video_id = self.request.get('v')
	if video_id:
		query = Video.all()
		query.filter("youtube_id =", video_id)
		video = query.get()
		
		query = VideoPlaylist.all()
		query.filter("video = ", video)
		video_playlists = query.fetch(5)
		
		colcount = 0 #used for formating on displayedpage
		rowcount = 0 #used for formating on displayedpage
		for video_playlist in video_playlists:
			query = VideoPlaylist.all()
			query.filter("playlist =", video_playlist.playlist)
			video_playlist.videos = query.fetch(500)
			
			video_count = 0 #used for formating on displayedpage
			rowcount = 0 #used for formating on displayedpage
			for videos_in_playlist in video_playlist.videos:
				video_count = video_count +1
				if video_count%3==0: #three video titles per row
					rowcount = rowcount+1
				if rowcount%2==0:
					videos_in_playlist.current_background = "highlightWhite" 
				else:
					videos_in_playlist.current_background = "highlightGreyRelated"
				
				if videos_in_playlist.video_position == video_playlist.video_position:
					videos_in_playlist.current_video = True
				else:
					videos_in_playlist.current_video = False
				if videos_in_playlist.video_position == video_playlist.video_position-1:
					video_playlist.previous_video = videos_in_playlist.video
				if videos_in_playlist.video_position == video_playlist.video_position+1:
					video_playlist.next_video = videos_in_playlist.video
		
		template_values = { 'video': video,
				    'video_playlists': video_playlists}
		path = os.path.join(os.path.dirname(__file__), "viewvideo.html")
		self.response.out.write(template.render(path, template_values))

class ViewExerciseVideos(webapp.RequestHandler):
    def get(self):
    	    user = users.get_current_user()
    	    if user:
    	    	    query = UserData.all()
		    query.filter("user =", user)
		    user_data = query.get()
		    
		    if user_data is None:
			user_data = UserData(user=user,last_login=datetime.datetime.now(),proficient_exercises=[],suggested_exercises=[],assigned_exercises=[],need_to_reassess=True, points=0)
			user_data.put()
			
    	    	    exkey = self.request.get('exkey')
    	    	    if exkey:
    	    	    	    exercise = Exercise.get(db.Key(exkey))
    	    	    	    query = ExerciseVideo.all()
    	    	    	    query.filter("exercise =", exercise.key())
    	 
    	    	    	    exercise_videos = query.fetch(50)
    	    	    	    
    	    	    	    logout_url = users.create_logout_url(self.request.uri)
			
    	    	    	    template_values = {
    	    	    	    	    'points': user_data.points,
    	    	    	    	    'username': user.nickname(),
    	    	    	    	    'logout_url': logout_url,
				    'exercise': exercise,
				    'first_video': exercise_videos[0].video,
				    'extitle': exercise.name.replace('_', ' ').capitalize(),
				    'exercise_videos': exercise_videos}
				    
		            path = os.path.join(os.path.dirname(__file__), "exercisevideos.html")
		            self.response.out.write(template.render(path, template_values))
    	    	    	    
    	    else:
    	    	    self.redirect(users.create_login_url(self.request.uri))   
	


class ExerciseAdminPage(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			query = Exercise.all().order("h_position")
			exercises = query.fetch(200)
			
			for exercise in exercises:
				exercise.display_name = exercise.name.replace('_',' ').capitalize()
			
			template_values = {'exercises': exercises}
			
			path = os.path.join(os.path.dirname(__file__), 'exerciseadmin.html')
			self.response.out.write(template.render(path, template_values))
			
		else:
    	    	    self.redirect(users.create_login_url(self.request.uri))
    	    	    
    	    	    
	    	    
    
class ViewMapExercises(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			
			query = UserData.all()
			query.filter("user =", user)
			user_data = query.get()
			
			knowledge_map_url = "/knowledgemap?"
			suggested_count = 0
			proficient_count = 0
			
			
			if user_data is None:
				user_data = UserData(user=user,last_login=datetime.datetime.now(),proficient_exercises=[],suggested_exercises=[],assigned_exercises=[],need_to_reassess=True, points=0)
				user_data.put()
				
			if user_data.need_to_reassess is True:
				self.redirect('/assessuser')
				
			query = UserExercise.all()
			query.filter("user =", user)
			user_exercises = query.fetch(200)
			
			query = Exercise.all().order("h_position")
			exercises = query.fetch(200)
			suggested_exercises = []
			for exercise in exercises:
				exercise.display_name = exercise.name.replace('_','&nbsp;').capitalize()
				exercise.proficient = False
				exercise.suggested = False
				exercise.assigned = False
				if exercise.name in user_data.proficient_exercises:
					exercise.proficient= True
					knowledge_map_url = knowledge_map_url+"&p"+str(proficient_count)+"="+exercise.name
					proficient_count = proficient_count + 1
				if exercise.name in user_data.assigned_exercises:
					exercise.assigned = True
					
				if exercise.name in user_data.suggested_exercises:
					exercise.suggested = True
					knowledge_map_url = knowledge_map_url+"&s"+str(suggested_count)+"="+exercise.name
					suggested_count = suggested_count + 1
				exercise.streak = 0
				for user_exercise in user_exercises:
					if user_exercise.exercise == exercise.name:
						exercise.streak = user_exercise.streak
						exercise.longest_streak = user_exercise.longest_streak
						exercise.total_done = user_exercise.total_done
						exercise.points = PointCalculator(exercise.streak,exercise.suggested,exercise.proficient)
						break
					else:
						exercise.points = PointCalculator(0,exercise.suggested,exercise.proficient)
				exercise.streakwidth = min(200, 20*exercise.streak)
				
				if exercise.suggested:
					suggested_exercises.append(exercise)
			
			logout_url = users.create_logout_url(self.request.uri)
			
			template_values = {'exercises': exercises,
					   'suggested_exercises':suggested_exercises,
					   'knowledge_map_url':knowledge_map_url,
				      	   'points':user_data.points,
					   'username': user.nickname(),
					   'logout_url': logout_url}
			
			path = os.path.join(os.path.dirname(__file__), 'viewknowledgemap.html')
			self.response.out.write(template.render(path, template_values))
			
		else:
    	    	    self.redirect(users.create_login_url(self.request.uri))
    	    	    
class ViewAllExercises(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			
			query = UserData.all()
			query.filter("user =", user)
			user_data = query.get()
			
			if user_data is None:
				user_data = UserData(user=user,last_login=datetime.datetime.now(),proficient_exercises=[],suggested_exercises=[],assigned_exercises=[],need_to_reassess=True, points=0)
				user_data.put()
				
			if user_data.need_to_reassess is True:
				self.redirect('/assessuser')
				
			query = UserExercise.all()
			query.filter("user =", user)
			user_exercises = query.fetch(200)
			
			query = Exercise.all().order("h_position")
			exercises = query.fetch(200)
			suggested_exercises = []
			for exercise in exercises:
				exercise.display_name = exercise.name.replace('_',' ').capitalize()
				exercise.proficient = False
				exercise.suggested = False
				exercise.assigned = False
				if exercise.name in user_data.proficient_exercises:
					exercise.proficient= True
				
				if exercise.name in user_data.assigned_exercises:
					exercise.assigned = True
					
				if exercise.name in user_data.suggested_exercises:
					exercise.suggested = True
					
				exercise.streak = 0
				for user_exercise in user_exercises:
					if user_exercise.exercise == exercise.name:
						exercise.streak = user_exercise.streak
						exercise.longest_streak = user_exercise.longest_streak
						exercise.total_done = user_exercise.total_done
						exercise.points = PointCalculator(exercise.streak,exercise.suggested,exercise.proficient)
						break
					else:
						exercise.points = PointCalculator(0,exercise.suggested,exercise.proficient)
				exercise.streakwidth = min(200, 20*exercise.streak)
				
				if exercise.suggested:
					suggested_exercises.append(exercise)
			
			logout_url = users.create_logout_url(self.request.uri)
			
			template_values = {'exercises': exercises,
					   'suggested_exercises':suggested_exercises,
				      	   'points':user_data.points,
					   'username': user.nickname(),
					   'logout_url': logout_url}
			
			path = os.path.join(os.path.dirname(__file__), 'viewexercises.html')
			self.response.out.write(template.render(path, template_values))
			
		else:
    	    	    self.redirect(users.create_login_url(self.request.uri))
    	    	 
class VideolessExercises(webapp.RequestHandler):
	def get(self):
		query = Exercise.all().order("h_position")
		exercises = query.fetch(200)
		self.response.out.write('<html>')
		for exercise in exercises:
			query = ExerciseVideo.all()
			query.filter("exercise =", exercise.key())
			videos = query.fetch(200)
			if not videos:
				self.response.out.write('<P><A href="/exercises?exid='+exercise.name+'">'+exercise.name+'</A>')
    	    	 
class KnowledgeMap(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			query = Exercise.all().order("h_position")
			exercises = query.fetch(200)
			
			proficient_exercises = []
			suggested_exercises = []
			
			proficient_count = 0
			proficient_exercise = self.request.get('p'+str(proficient_count))
			while proficient_exercise:
				proficient_exercises.append(proficient_exercise)
				proficient_count = proficient_count + 1
				proficient_exercise = self.request.get('p'+str(proficient_count))
			
			suggested_count = 0
			suggested_exercise = self.request.get('s'+str(suggested_count))
			while suggested_exercise:
				suggested_exercises.append(suggested_exercise)
				suggested_count = suggested_count + 1
				suggested_exercise = self.request.get('s'+str(suggested_count))
			
			
			for exercise in exercises:
				exercise.suggested = False
				exercise.proficient = False
				if exercise.name in suggested_exercises:
					exercise.suggested = True
				if exercise.name in proficient_exercises:
					exercise.proficient = True
				name = exercise.name.capitalize()
				name_list = name.split('_')
				exercise.display_name = str(name_list).replace("[u'", "['").replace(", u'", ", '")
				exercise.prereq_string = str(exercise.prerequisites).replace("[u'", "['").replace(", u'", ", '")
				
			logout_url = users.create_logout_url(self.request.uri)
			
			template_values = {'exercises': exercises,
						'logout_url': logout_url,
						'map_height':900}
			
			path = os.path.join(os.path.dirname(__file__), 'knowledgemap.html')
			self.response.out.write(template.render(path, template_values))
			
		else:
    	    	    self.redirect(users.create_login_url(self.request.uri))
    	 
    	    	 
    	    	    
class EditExercise(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			exercise_name = self.request.get('name')
			if (exercise_name):
				query = Exercise.all().order("h_position")
				exercises = query.fetch(200)
			
				main_exercise= None
				for exercise in exercises:
					exercise.display_name = exercise.name.replace('_',' ').capitalize()
					if exercise.name==exercise_name:
						main_exercise = exercise
				
				query = ExercisePlaylist.all()
				query.filter("exercise =", main_exercise.key())
				exercise_playlists = query.fetch(50)
				
				query = Playlist.all()
				all_playlists = query.fetch(50)
				
				query = ExerciseVideo.all()
				query.filter("exercise =", main_exercise.key())
				exercise_videos = query.fetch(50)
				
				videos = []

				playlist_videos = None
				for exercise_playlist in exercise_playlists:
					query = VideoPlaylist.all()
					query.filter("playlist =", exercise_playlist.playlist.key())
					query.order('video_position')
					playlist_videos = query.fetch(200)
					for playlist_video in playlist_videos:
						videos.append(playlist_video.video)
			
				
				
				template_values = {'exercises': exercises,
							'exercise_playlists': exercise_playlists,
							'all_playlists': all_playlists,
							'exercise_videos': exercise_videos,
							'playlist_videos': playlist_videos,
							'videos': videos,
							'main_exercise':main_exercise}
				
				path = os.path.join(os.path.dirname(__file__), 'editexercise.html')
				self.response.out.write(template.render(path, template_values))
			
		else:
    	    	    self.redirect(users.create_login_url(self.request.uri))
    	    	    
class UpdateExercise(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if users.is_current_user_admin():
			exercise_name = self.request.get('name')
			if (exercise_name):
				query = Exercise.all()
				query.filter("name =", exercise_name)
				exercise = query.get()
				if (not exercise):
					exercise = Exercise(name=exercise_name)
					exercise.prerequisites = []
					exercise.covers = []
					
					
				add_prerequisite = self.request.get('add_prerequisite')
				delete_prerequisite = self.request.get('delete_prerequisite')
				add_covers = self.request.get('add_covers')
				delete_covers = self.request.get('delete_covers')
				v_position = self.request.get('v_position');
				h_position = self.request.get('h_position');
				
				add_video = self.request.get('add_video')
				delete_video = self.request.get('delete_video')
				add_playlist = self.request.get('add_playlist')
				delete_playlist = self.request.get('delete_playlist')
				
				if (add_prerequisite):
					if (add_prerequisite not in exercise.prerequisites):
						exercise.prerequisites.append(add_prerequisite)
				if (delete_prerequisite):
					if (delete_prerequisite in exercise.prerequisites):
						exercise.prerequisites.remove(delete_prerequisite)
				if (add_covers):
					if (add_covers not in exercise.covers):
						exercise.covers.append(add_covers)
				if (delete_covers):
					if (delete_covers in exercise.covers):
						exercise.covers.remove(delete_covers)	
				if (v_position):
					exercise.v_position = int(v_position)
				if (h_position):
					exercise.h_position = int(h_position)
					
				if add_video:
					query = ExerciseVideo.all()
					query.filter("video =", db.Key(add_video))
					query.filter("exercise =", exercise.key())
					exercise_video = query.get()
					if not exercise_video:
						exercise_video = ExerciseVideo()
						exercise_video.exercise = exercise
						exercise_video.video = db.Key(add_video)
						exercise_video.put()
				if delete_video:
					query = ExerciseVideo.all()
					query.filter("video =", db.Key(delete_video))
					query.filter("exercise =", exercise.key())
					exercise_videos = query.fetch(200)
					for exercise_video in exercise_videos:
						exercise_video.delete()
						
				if add_playlist:
					query = ExercisePlaylist.all()
					query.filter("playlist =", db.Key(add_playlist))
					query.filter("exercise =", exercise.key())
					exercise_playlist = query.get()
					if not exercise_playlist:
						exercise_playlist = ExercisePlaylist()
						exercise_playlist.exercise = exercise
						exercise_playlist.playlist = db.Key(add_playlist)
						exercise_playlist.put()
						
				if delete_playlist:
					query = ExercisePlaylist.all()
					query.filter("playlist =", db.Key(delete_playlist))
					query.filter("exercise =", exercise.key())
					exercise_playlists = query.fetch(200)
					for exercise_playlist in exercise_playlists:
						exercise_playlist.delete()
				
				
				exercise.put()
				
				if (v_position or h_position):
					self.redirect('/admin94040')
				else:
					self.redirect('/editexercise?name='+exercise_name)
		else:
    	    	    self.redirect(users.create_login_url(self.request.uri))

class GraphPage(webapp.RequestHandler):
    def get(self):
    	    width = self.request.get('w')
    	    height = self.request.get('h')
    	    template_values = {
    	    	    	'width': width,
    	    	    	'height': height }
    	    	    	
    	    path = os.path.join(os.path.dirname(__file__), 'graphpage.html')
    	    self.response.out.write(template.render(path, template_values))


class AssessUser(webapp.RequestHandler):
    def noRepeatListMerge(self,a,b):
    	    for x in a:
    	    	    if x not in b:
    	    	    	    b.append(x)
    	    return b

    def getCoveredSubjects(self,exercise, exercise_list):
    	     covers = exercise.covers
    	     for covered_exid in covers:
    	     	     for e in exercise_list:
    	     	     	     if e.name == covered_exid:
    	     	     	     	     covers = self.noRepeatListMerge(covers,self.getCoveredSubjects(e,exercise_list))
    	     	     	     	     break
    	     return covers
	
    def get(self):
    	    user = users.get_current_user()
    	    if user:
    	    	    query = UserData.all()
		    query.filter("user =", user)
		    user_data = query.get()
			
		    if user_data is None:
		    	    user_data = UserData(user=user,last_login=datetime.datetime.now(),proficient_exercises=[],suggested_exercises=[],assigned_exercises=[])
		    
		    query = Exercise.all()
		    exercises = query.fetch(200)
		    
		    suggested = []
		    proficient = user_data.proficient_exercises
		    covered_by_proficient = user_data.proficient_exercises
		    """
		    for exid in proficient:
		    	    for e in exercises:
		    	    	    if e.name == exid:
		    	    	    	    new_covered = self.getCoveredSubjects(e, exercises)
		    	    	    	    covered_by_proficient = self.noRepeatListMerge(covered_by_proficient, new_covered)
		    	    	    	    break;
		    """
		    for exercise in exercises:
			    all_prerequisites_covered = True
			    if exercise.name not in covered_by_proficient:
			    	    for prerequisite in exercise.prerequisites:
			    	    	    if prerequisite not in covered_by_proficient:
			    	    	    	    all_prerequisites_covered = False
			    	    	    	    break
			    	    if all_prerequisites_covered:
			    	    	    suggested.append(exercise.name)
		    user_data.suggested_exercises = suggested
		    user_data.need_to_reassess = False
		    user_data.put()
    	    	    
    	    	    self.redirect('/')
    	    else:
    	    	    self.redirect(users.create_login_url(self.request.uri))






class TestAssessUser(webapp.RequestHandler):
    def noRepeatListMerge(self,a,b):
    	    for x in a:
    	    	    if x not in b:
    	    	    	    b.append(x)
    	    return b

    def getCoveredSubjects(self,exercise, exercise_list, depth):
    	    
    	     covers = exercise.covers
    	     self.response.out.write('<P>getCoveredSubjects: '+exercise.name)
    	     self.response.out.write('<br>depth: '+str(depth))
    	     self.response.out.write('<br>covered: '+str(covers))
    	     if depth>4:
    	     	     return covers
    	     else:
		     
		     for covered_exid in covers:
			     for e in exercise_list:
				     if e.name == covered_exid:
				     	     self.response.out.write('<br>'+e.name+' covers '+str(e.covers))
					     covers = self.noRepeatListMerge(covers,self.getCoveredSubjects(e,exercise_list,depth+1))
					     break
		     return covers
	
    def get(self):
    	    self.response.out.write('<html>')
    	    
    	    username = self.request.get('u')
    	    self.response.out.write('<P><B>Test Assess</B>, username:'+username)
    	    user_data = None
    	    query = UserData.all()
    	    for entry in query:
    	    	    if entry.user.nickname()==username:
    	    	    	    user_data = entry
    	    	    	    break
    	
	    query = Exercise.all()
	    exercises = query.fetch(200)
	    
	    suggested = []
	    proficient = user_data.proficient_exercises
	    covered_by_proficient = user_data.proficient_exercises
	    
	    for exid in proficient:
		    for e in exercises:
			    if e.name == exid:
			    	    self.response.out.write('<P>'+e.name+' covers '+str(e.covers))
				    new_covered = self.getCoveredSubjects(e, exercises,0)
				    self.response.out.write('<P>New Covered: '+str(new_covered))
				    covered_by_proficient = self.noRepeatListMerge(covered_by_proficient, new_covered)
				    self.response.out.write('<P>Covered by proficient: '+str(covered_by_proficient))
				    break;
				    
	    for exercise in exercises:
		    all_prerequisites_covered = True
		    if exercise.name not in covered_by_proficient:
			    for prerequisite in exercise.prerequisites:
				    if prerequisite not in covered_by_proficient:
					    all_prerequisites_covered = False
					    break
			    if all_prerequisites_covered:
				    suggested.append(exercise.name)
	    user_data.suggested_exercises = suggested
	    user_data.need_to_reassess = False
	   

class AdminViewUser(webapp.RequestHandler):
	def get(self):
    	    username = self.request.get('u')
    	    if username:
    	    	    
    	    	    
    	    	    userdata = None
    	    	    exercisedata = None
    	    	    query = UserData.all()
    	    	    for user_data in query:
    	    	    	    if user_data.user.nickname()==username:
    	    	    	    	 userdata =user_data
    	    	    		 query = UserExercise.all()
    	    	    		 query.filter("user =", userdata.user)
    	    	    		 exercisedata = query.fetch(300)
    	    	    		 break
    	    	    		
    	    	    template_values = {'exercise_data': exercisedata,
    	    	    		 	'user_data': userdata }   	    
    	    	    path = os.path.join(os.path.dirname(__file__), 'adminviewuser.html')
    	    	    self.response.out.write(template.render(path, template_values))

class RegisterAnswer(webapp.RequestHandler):
    def post(self):
    	    user = users.get_current_user()
    	    if user:
    	    	    key = self.request.get('key')
    	    	    exid = self.request.get('exid')
    	    	    correct = int(self.request.get('correct'))
    	    	    start_time = float(self.request.get('start_time'))
    	    	    
    	    	    elapsed_time = int(float(time.time())-start_time)
    	    	    
    	    	    problem_log = ProblemLog()
    	    	    problem_log.user = user
    	    	    problem_log.exercise = exid
    	    	    problem_log.correct = False
    	    	    if correct==1:
    	    	    	    problem_log.correct = True
    	    	    problem_log.time_done = datetime.datetime.now()
    	    	    problem_log.time_taken = elapsed_time
    	    	    problem_log.put()
    	    	    
    	    	    
    	    	    
    	    	    
    	    	    userExercise = db.get(key)
    	    	    userExercise.last_done = datetime.datetime.now()
    	    	    
    	    	    query = UserData.all()
    	    	    query.filter("user =", userExercise.user)
    	    	    user_data = query.get()
    	    	    suggested = exid in user_data.suggested_exercises
    	    	    proficient = exid in user_data.proficient_exercises
    	    	    if user_data.points == None:
    	    	    	user_data.points = 0
    	    	    user_data.points = user_data.points + PointCalculator(userExercise.streak,suggested,proficient)
    	    	    user_data.put()
    	    	    
    	    	    if (userExercise.total_done):
    	    	    	    userExercise.total_done = userExercise.total_done+1
    	    	    else:
    	    	    	    userExercise.total_done=1
    	    	    now_proficient_string = ""
    	    	    if (correct==1):
    	    	    	    userExercise.streak = userExercise.streak+1
    	    	    	    if (userExercise.streak > userExercise.longest_streak):
    	    	    	    	    userExercise.longest_streak = userExercise.streak
    	    	    	    	    if userExercise.streak==10:
    	    	    	    	    	    now_proficient_string = "&proficient=1"
    	    	    	    	    	    query = UserData.all()
    	    	    	    	    	    query.filter("user =", user)
    	    	    	    	    	    user_data = query.get()
    	    	    	    	    	    if user_data is None:
    	    	    	    	    	    	    user_data = UserData(user=user,last_login=datetime.datetime.now(),proficient_exercises=[],suggested_exercises=[],assigned_exercises=[])
    	    	    	    	    	    	    
					    if userExercise.exercise not in user_data.proficient_exercises:
					    	    user_data.proficient_exercises.append(userExercise.exercise)
					    user_data.need_to_reassess = True
    	    	    	    	    	    user_data.put()
    	    	    else:
    	    	    	    userExercise.streak =0
    	    	    	    
    	    	    
    	    	    userExercise.put()
    	    	    
    	    	    self.redirect('/exercises?exid='+exid+now_proficient_string)
    	    else:
    	    	    self.redirect(users.create_login_url(self.request.uri))
    	    	   
class ViewUsers(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			query = UserData.all()
			count = 0
			for user in query:
				count = count+1
				
			self.response.out.write('Users '+str(count))
			
			
			#template_values = {'users': all_users}
			
			#path = os.path.join(os.path.dirname(__file__), 'viewusers.html')
			#self.response.out.write(template.render(path, template_values))
			
		else:
    	    	    self.redirect(users.create_login_url(self.request.uri))
    	    	     
    	    	    
class ViewVideoLibrary(webapp.RequestHandler):
	def get(self):
		colOne = []
		colOne.append("Algebra 1")
		colOne.append("Algebra")
		colOne.append("California Standards Test: Algebra I") 
		colOne.append("California Standards Test: Algebra II")
		colOne.append("Arithmetic")
		colOne.append("Pre-algebra")
		colOne.append("Geometry")
		colOne.append("California Standards Test: Geometry")
		
		colTwo = []
		colTwo.append("Chemistry")
		
		colTwo.append("Brain Teasers")
		colTwo.append("Current Economics")
		colTwo.append("Banking and Money")
		colTwo.append("Venture Capital and Capital Markets")
		colTwo.append("Finance")
		colTwo.append("Valuation and Investing")
		colTwo.append("Credit Crisis")
		colTwo.append("Geithner Plan")
		colTwo.append("Paulson Bailout")
		
	
	
		colThree = []
		colThree.append("Biology")
		colThree.append("Trigonometry")
		colThree.append("Precalculus")
		colThree.append("Statistics")
		colThree.append("Probability")
		colThree.append("Calculus")
		colThree.append("Differential Equations")
		
		colFour = []
		colFour.append("History")
		colFour.append("Linear Algebra")
		colFour.append("Physics")
		
		cols = [colOne, colTwo, colThree, colFour]
		
		columns = []
		for column in cols:
			new_column = []
			for playlist_title in column:
				query = Playlist.all()
				query.filter("title =", playlist_title)
				playlist = query.get()
				query = VideoPlaylist.all()
				query.filter("playlist =", playlist)
				query.order('video_position')
				playlist_videos = query.fetch(500)
				self.response.out.write(' '+str(len(playlist_videos))+' retrieved for '+playlist_title+' ')
				new_column.append(playlist_videos)
			columns.append(new_column)
		
		
		#Separating out the columns because the formatting is a little different on each column
		template_values = {'c1': columns[0],
				   'c2': columns[1],
				   'c3': columns[2],
				   'c4': columns[3],
				   'playlist_names': cols}   	    
    	    	path = os.path.join(os.path.dirname(__file__), 'videolibrary.html')
    	    	self.response.out.write(template.render(path, template_values))
				

def main():
  webapp.template.register_template_library('templatefilters')
  application = webapp.WSGIApplication([('/', ViewAllExercises),
  	  				('/library', ViewVideoLibrary),
  	  				('/syncvideodata', UpdateVideoData),
  	  				('/singleplaylistsync', UpdatePlaylistVideoData),
  	  				('/exercises', ViewExercise),
  	  				('/assessuser', AssessUser),
  	  				('/testassess', TestAssessUser),
  	  				('/editexercise', EditExercise),
  	  				('/deletevideoplaylists', DeleteVideoPlaylists),
  	  				('/viewexercisevideos', ViewExerciseVideos),
  	  				('/knowledgemap', KnowledgeMap),
  	  				('/viewexercisesonmap', ViewMapExercises),
  	  				('/testdatastore', DataStoreTest),
  	  				 ('/admin94040', ExerciseAdminPage),
  	  				 ('/adminusers', ViewUsers),
  	  				 ('/videoless', VideolessExercises),
  	  				 ('/adminuserdata', AdminViewUser),
  	  				 ('/updateexercise', UpdateExercise),
  	  				 ('/graphpage.html', GraphPage),
  	  				 ('/registeranswer', RegisterAnswer),
  	  				 ('/video', ViewVideo),
  	  				 ('/qbrary', qbrary.MainPage), #here and below are all qbrary related pages
  	  				 ('/subjectmanager', qbrary.SubjectManager),
  	  				 ('/editsubject', qbrary.CreateEditSubject),
  	  				 ('/viewsubject', qbrary.ViewSubject),
  	  				 ('/deletequestion', qbrary.DeleteQuestion),
  	  				 ('/deletesubject', qbrary.DeleteSubject),
  	  				 ('/changepublished', qbrary.ChangePublished),
  	  				 ('/pickquestiontopic', qbrary.PickQuestionTopic),
  	  				 ('/pickquiztopic', qbrary.PickQuizTopic),
  	  				 ('/answerquestion', qbrary.AnswerQuestion),
  	  				 ('/rating', qbrary.Rating),
  	  				 ('/viewquestion', qbrary.ViewQuestion),
  	  				 ('/editquestion', qbrary.CreateEditQuestion),
  	  				 ('/addquestion', qbrary.CreateEditQuestion)],
  	  				 debug=True)
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
