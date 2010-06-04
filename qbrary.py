import os
from google.appengine.ext.webapp import template
import random
import logging

import cgi

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

class Greeting(db.Model):
  author = db.UserProperty()
  content = db.StringProperty(multiline=True)
  date = db.DateTimeProperty(auto_now_add=True)
  

class Subject(db.Model):
	author = db.UserProperty()
	name = db.StringProperty()
	parent_subject = db.SelfReferenceProperty()
	index = db.IntegerProperty()  #to order a child subject within a parent subject
	
			
	
class Question(db.Model):
	author = db.UserProperty()
	subject = db.ReferenceProperty(Subject)
	question_text = db.TextProperty()
	correct_choice_text = db.TextProperty()
	incorrect_1 = db.TextProperty()
	incorrect_2 = db.TextProperty()
	incorrect_3 = db.TextProperty()
	incorrect_4 = db.TextProperty()
	incorrect_5 = db.TextProperty()
	answer_text = db.TextProperty()
	date_created = db.DateTimeProperty(auto_now_add=True)
	published = db.BooleanProperty()
	not_completed = db.BooleanProperty() #Test's if the user actually didn't completed the creation process
	answer_count = db.IntegerProperty()
	correct_count = db.IntegerProperty()
	avg_importance = db.RatingProperty()
	avg_difficulty = db.RatingProperty()
	avg_quality = db.RatingProperty()
	hint_text = db.TextProperty()
	
	
class QuestionAnswerer(db.Model):
	answerer = db.UserProperty()
	question = db.ReferenceProperty(Question)
	correct_count = db.IntegerProperty()
	total_count = db.IntegerProperty()
	last_done = db.DateTimeProperty()
	importance_rating = db.RatingProperty()
	importance_width = db.IntegerProperty() #used for the pixel width of the actual stars
	difficulty_rating = db.RatingProperty()
	difficulty_width = db.IntegerProperty() #used for the pixel width of the actual stars
	quality_rating = db.RatingProperty()
	quality_width = db.IntegerProperty() #used for the pixel width of the actual stars
	

class AnswerLog(db.Model):
	answer_author = db.UserProperty()
	question = db.ReferenceProperty(Question)
	tries = db.IntegerProperty()
	date = db.DateTimeProperty(auto_now_add=True)

def breadcrumb(subj):
	b = []
	parent_subject = subj.parent_subject
	while parent_subject:
		if parent_subject.parent_subject: #don't want to add the root
			b.append(parent_subject)
		parent_subject = parent_subject.parent_subject
	b.reverse()
	return b
	
def subtopics(subj):
	return Subject.gql("WHERE parent_subject = :1 ORDER BY index", subj)
	
	
def childBranches(subject):
	topics = subtopics(subject)
	branch = []
	if st:
		for topic in topics:
			branch.append([topic, childBranches(topic)])
		return branch
	else:
		return []
		
def htmlChildren(subject):
	output = "<B>"+subject.name+"</B>"

	s_topics = subtopics(subject)
	if s_topics.count()<1:
		output = output + " | <A href='/addquestion?subject_key="+subject.key().__str__()+"'>Add Question</a><br>"
	else:
		output = output + "<UL>"
		for topic in s_topics:
			output = output + "<LI>"+htmlChildren(topic)+"</LI>"
		output = output + "</UL>"
	
	return output
		

	
def pickQuestionTopicHTML(subject):
	output = "<B>"+subject.name+"</B>"

	s_topics = subtopics(subject)
	if s_topics.count()<1:
		output = "<A href='/addquestion?subject_key="+subject.key().__str__()+"'><B>"+subject.name+"</B></a><br>"
	else:
		output = output + "<UL>"
		for topic in s_topics:
			output = output + "<LI>"+pickQuestionTopicHTML(topic)+"</LI>"
		output = output + "</UL>"
	
	return output
	
def pickQuizTopicHTML(subject):
	output = "<A href='/answerquestion?subject_key="+subject.key().__str__()+"'><B>"+subject.name+"</B></a><br>"
	
	s_topics = subtopics(subject)
	if s_topics.count()>0:
		output = output + "<UL>"
		for topic in s_topics:
			output = output + "<LI>"+pickQuizTopicHTML(topic)+"</LI>"
		output = output + "</UL>"
	
	return output

#Returns a list of the most granular subtopics within a topic
def getBottomLevelChildren(subj):
	output = []
	s_topics = subtopics(subj)
	if s_topics.count()<1:
		output=[subj]
	else:
		for topic in s_topics:
			output.extend(getBottomLevelChildren(topic))
	return output
	
class DeleteSubject(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		subject_key = self.request.get('subject_key')
		subject = db.get(subject_key)
		redirect_url = self.request.get('redirect')
		if user:
			if user==subject.author:
				subject.delete()
			self.redirect(redirect_url)
		else:
			self.redirect(users.create_login_url(self.request.uri))	

class DeleteQuestion(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		question_key = self.request.get('question_key')
		question = db.get(question_key)
		redirect_url = self.request.get('redirect')
		if user:
			if user==question.author:
				question.delete()
			self.redirect(redirect_url)
		else:
			self.redirect(users.create_login_url(self.request.uri))
			
class ChangePublished(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		question_key = self.request.get('question_key')
		question = db.get(question_key)
		redirect_url = self.request.get('redirect')
		if user:
			if user==question.author:
				if (question.published):
					question.published = None
				else:
					question.published = True
				question.put()
			self.redirect(redirect_url)
		else:
			self.redirect(users.create_login_url(self.request.uri))
	

class MainPage(webapp.RequestHandler):
	def get(self):
	
		user = users.get_current_user()
		if user:
			#Do a SQL query to select the root subject (it has no parent)
			subs = Subject.gql("WHERE parent_subject=:1", None) 
			#We need at least the root subject
			if subs.count() <1:
				root= Subject()
				root.author = user
				root.name = 'root'
				root.put()
			else:
				root = subs[0]
				
				
			#select all of the children of the root subject to 
			subjects = Subject.gql("WHERE parent_subject = :1", root)
			
			#select all of the questions that the user has created
			published = Question.gql("WHERE author = :1 and published = :2 and not_completed = :3", user, True, False)
			notpublished = Question.gql("WHERE author = :1 and published = :2 and not_completed = :3", user, None, False)
			greeting = ("user: %s [<a href=\"%s\">sign out</a>]" %
					(user.nickname(), users.create_logout_url("/")))

			
			template_values = {
				'subjects': subjects,
				'greeting': greeting,
				'published': published,
				'notpublished': notpublished,
				'current_url': self.request.uri,
				'user': user
			}
			
			path = os.path.join(os.path.dirname(__file__), 'myprofile.html')
			self.response.out.write(template.render(path, template_values))
				
		else:
			self.redirect(users.create_login_url(self.request.uri))

class CreateEditSubject(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		#This if/then clause just makes sure that the user is logged in
		if  user:
			subject_key = self.request.get('subject_key')
			subject_name = self.request.get('subject_name') #Get this if editing name of subject
			child_name = self.request.get('child_name') #Get this if adding child to subject
			
			#Get the subject key if we are editing its name or adding a child
			#I think this will always be the case so we may want to get rid of the if/then clause and
			#just do the if part
			if subject_key:
				subject = db.get(subject_key)
			else:
				subject = Subject(author=user)
				
			st = subtopics(subject)
			next_index = st.count()+1
				
			#This is the case that someone has created or changed a subject's name (forwards back to profile page)
			#This subject has no parent and no index
			if subject_name: 
				subject.name = subject_name
				subject.put()
				self.redirect('/qbrary')
			
			else:
				#This is the case the someone is adding a subtopic to this subject
				if child_name:
					child_subject = Subject()
					child_subject.author = user
					child_subject.name = child_name
					child_subject.parent_subject = subject
					child_subject.index = next_index
					child_subject.put()
					st = subtopics(subject)
					#subtopics = Subject.gql("WHERE parent_subject = :1 ORDER BY index", subject)
				
				bc = breadcrumb(subject)
				html_tree = htmlChildren(subject)
				
				root = Subject.gql("WHERE parent_subject=:1", None).get()
				subjects = Subject.gql("WHERE parent_subject = :1", root)
				greeting = ("user: %s [<a href=\"%s\">sign out</a>]" %
					(user.nickname(), users.create_logout_url("/")))
			
				
				template_values = {	'subject':subject,
							'subjects': subjects,
							'greeting': greeting,
						    	'subtopics':st,
							'tree': html_tree,
							'breadcrumb':bc,
                                                        'redirect_url' : self.request.uri}
				path = os.path.join(os.path.dirname(__file__), 'editsubject.html')
				self.response.out.write(template.render(path, template_values))
			
			
		else:
			self.redirect(users.create_login_url(self.request.uri))
			
class ViewSubject(webapp.RequestHandler):
	def get(self):  
		user = users.get_current_user()	
		if  user:
			subject_key = self.request.get('subject_key')
			if subject_key:
				subject = db.get(subject_key)
				html_tree = htmlChildren(subject)
				template_values = {'subject':subject,
							'tree':html_tree}
				path = os.path.join(os.path.dirname(__file__), 'viewsubject.html')
				self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(users.create_login_url(self.request.uri))

class Rating(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()	
		if  user:
			user_question_key = self.request.get('key')
			difrating = self.request.get('difrating')
			qualrating = self.request.get('qualrating')
			imprating = self.request.get('imprating')
			if (user_question_key):
				user_question = db.get(user_question_key)
				#if user==user_question.answerer:
				if difrating:
					difrating = int(difrating)
					user_question.difficulty_rating = difrating
					user_question.difficulty_width = difrating*20
					user_question.put()
					rating_type='difficulty'
					rating = difrating
					rating_width = difrating*20
				if imprating:
					imprating = int(imprating)
					user_question.importance_rating = imprating
					user_question.importance_width = imprating*20
					user_question.put()
					rating_type='importance'
					rating = imprating
					rating_width = imprating*20
				if qualrating:
					qualrating = int(qualrating)
					user_question.quality_rating = qualrating
					user_question.quality_width = qualrating*20
					user_question.put()
					rating_type='quality'
					rating = qualrating
					rating_width = qualrating*20
					
				template_values = {'user_question': user_question,
						   'rating': rating,
						   'rating_width': rating_width,
						   'rating_type': rating_type}
				path = os.path.join(os.path.dirname(__file__), 'rating.html')
				self.response.out.write(template.render(path, template_values))
						
					
	
			
class AnswerQuestion(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()	
		if  user:
			subject_key = self.request.get('subject_key')
			if subject_key:
				root = Subject.gql("WHERE parent_subject=:1", None).get()
				subjects = Subject.gql("WHERE parent_subject = :1", root)
				greeting = ("user: %s [<a href=\"%s\">sign out</a>]" %
						(user.nickname(), users.create_logout_url("/")))
				
                                # get all questions that are in some subtopic of given subject
				subject = db.get(subject_key)
				children = getBottomLevelChildren(subject)
				questions = []
				for subj in children:
					questions.extend(Question.gql("WHERE subject=:1 and published =:2", subj, True))
					
				
					
				if len(questions)>0 :	
					question = random.choice(questions)
					
					untested_warning = (QuestionAnswerer.gql("WHERE question=:1", question)).count() < 5	 # TODO: clean this up
					
					answerer_question = (QuestionAnswerer.gql("WHERE answerer=:1 and question=:2", user, question)).get()

                                        # check if current user has answered the question before
                                        # create new QuestionAnswerer entry if they haven't
					if not answerer_question:
						answerer_question = QuestionAnswerer()
						answerer_question.answerer=user
						answerer_question.question=question
						answerer_question.difficulty_rating = 0
						answerer_question.quality_rating = 0
						answerer_question.importance_rating = 0
						answerer_question.difficulty_width = 0
						answerer_question.quality_width = 0
						answerer_question.importance_width = 0
						answerer_question.put()
				
					all_incorrect = [question.incorrect_1, 
							question.incorrect_2,
							question.incorrect_3,
							question.incorrect_4,
							question.incorrect_5]
					#need to randomly take out 4 of the incorrect choices
					choices = random.sample(all_incorrect,4)
					correct_index = random.randint(0,4)
					choices.insert(correct_index, question.correct_choice_text)
					choice0 = choices[0]
					choice1 = choices[1]
					choice2 = choices[2]
					choice3 = choices[3]
					choice4 = choices[4]
					

				
					template_values = {'subject':subject,
							'subjects': subjects,
							'greeting': greeting,
							'user_question': answerer_question,
							'correct_index': correct_index,
							'choice0': choice0,
							'choice1': choice1,
							'choice2': choice2,
							'choice3': choice3,
							'choice4': choice4,
							'question':question,
							'untested_warning':untested_warning}
					path = os.path.join(os.path.dirname(__file__), 'answerquestion.html')
					self.response.out.write(template.render(path, template_values))
				else:
					template_values = {'subject':subject,
							'subjects': subjects,
							'greeting': greeting}
					path = os.path.join(os.path.dirname(__file__), 'noquestion.html')
					self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(users.create_login_url(self.request.uri))
			
				
	
		
	
class ViewQuestion(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		#This if/then clause just makes sure that the user is logged in
		if  user:
			question_key = self.request.get('question_key')
			if question_key:
				question = db.get(question_key)
				bc = breadcrumb(question.subject)
				root = Subject.gql("WHERE parent_subject=:1", None).get()
				subjects = Subject.gql("WHERE parent_subject = :1", root)
				greeting = ("user: %s [<a href=\"%s\">sign out</a>]" %
					(user.nickname(), users.create_logout_url("/")))
			

				template_values = {'question':question,
							'subjects': subjects,
							'greeting': greeting,
							'current_url': self.request.uri,
							'breadcrumb': bc}
				path = os.path.join(os.path.dirname(__file__), 'viewquestion.html')
				self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(users.create_login_url(self.request.uri))
				
class PickQuestionTopic(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()	
		if  user:
			root = Subject.gql("WHERE parent_subject=:1", None).get()
			subjects = Subject.gql("WHERE parent_subject = :1", root)
			greeting = ("user: %s [<a href=\"%s\">sign out</a>]" %
					(user.nickname(), users.create_logout_url("/")))
			
			subject_key = self.request.get('subject_key')
			if subject_key:
				subject = db.get(subject_key)
				html_tree = pickQuestionTopicHTML(subject)
				template_values = {'subject':subject,
						   'subjects': subjects,
						   'greeting': greeting,
						   'tree':html_tree}
				path = os.path.join(os.path.dirname(__file__), 'pickquestiontopic.html')
				self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(users.create_login_url(self.request.uri))

class PickQuizTopic(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()	
		if  user:
			subject_key = self.request.get('subject_key')
			if subject_key:
				subject = db.get(subject_key)
				root = Subject.gql("WHERE parent_subject=:1", None).get()
				subjects = Subject.gql("WHERE parent_subject = :1", root)
				greeting = ("user: %s [<a href=\"%s\">sign out</a>]" %
					(user.nickname(), users.create_logout_url("/")))
			
				html_tree = pickQuizTopicHTML(subject)
				template_values = {'subject':subject,
						   'subjects': subjects,
						   'greeting': greeting,
						   'tree':html_tree}
				path = os.path.join(os.path.dirname(__file__), 'pickquiztopic.html')
				self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(users.create_login_url(self.request.uri))

			
			
class SubjectManager(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		#This if/then clause just makes sure that the user is logged in
		if  user:
			subs = Subject.gql("WHERE parent_subject=:1", None) 
			#We need at least the root subject
			if subs.count() <1:
				root= Subject()
				root.author = user
				root.name = 'root'
				root.put()
			else:
				root = subs[0]
				
			self.redirect('/editsubject?subject_key='+root.key().__str__())
		else:
			self.redirect(users.create_login_url(self.request.uri))


class CreateEditQuestion(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		#This if/then clause just makes sure that the user is logged in
		if  user:
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
			
			#If we are creating a new question, we need the subject
			subject_key = self.request.get('subject_key')
			#If we are editing/updating a previously created question, we need to be passed the key
			question_key = self.request.get('question_key')
			#If question_text is set, then we have to update the question
			question_text = self.request.get('question_text')
			
			# if true, then update the question and forward to viewquestion
			if question_text:
				question = db.get(question_key)
				if (question.author==user): #This here to make sure that someone can't hack someone else's question
					question.question_text = question_text
					question.correct_choice_text = self.request.get('correct_choice_text')
					question.incorrect_1=self.request.get('incorrect_1')
					question.incorrect_2=self.request.get('incorrect_2')
					question.incorrect_3=self.request.get('incorrect_3')
					question.incorrect_4=self.request.get('incorrect_4')
					question.incorrect_5=self.request.get('incorrect_5')
					question.answer_text = self.request.get('answer_text')
                                        question.hint_text = self.request.get('hint_text')
					question.not_completed = False
					question.put()
					self.redirect('/qbrary')

			#If we have a key, then we can retrieve the question; otherwise 
			#need to create a new one
			if question_key:
				question = db.get(question_key)
				mode_text = 'Edit Question'
				button_text = 'Save Updates'
				message_text = ' '
				
			else:
				question = Question(author=user)
				question.not_completed = True
				question.subject = db.get(subject_key)
				question.question_text=""
				question.correct_choice_text=""
				question.incorrect_1=""
				question.incorrect_2=""
				question.incorrect_3=""
				question.incorrect_4=""
				question.incorrect_5=""
				question.answer_text=""
                                question.hint_text = "" 
				question.put()
				mode_text = 'Add Question'
				button_text = 'Create Question'
				message_text = 'Step 2: Write the question...'
			
			bc = breadcrumb(question.subject)
			
			root = Subject.gql("WHERE parent_subject=:1", None).get()
			subjects = Subject.gql("WHERE parent_subject = :1", root)
			greeting = ("user: %s [<a href=\"%s\">sign out</a>]" %
					(user.nickname(), users.create_logout_url("/")))
			
			template_values = {	'question':question,
						'breadcrumb': bc,
						'message_text': message_text,
						'subjects': subjects,
						'greeting': greeting,
						'button_text': button_text,
						'mode_text':mode_text}
			path = os.path.join(os.path.dirname(__file__), 'editquestion.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(users.create_login_url(self.request.uri))
		
		

		
		
		
    
    
class Guestbook(webapp.RequestHandler):
  def post(self):
    greeting = Greeting()

    if users.get_current_user():
      greeting.author = users.get_current_user()

    greeting.content = self.request.get('content')
    greeting.put()
    self.redirect('/')

application = webapp.WSGIApplication(
                                     [('/', MainPage),
				      ('/subjectmanager', SubjectManager),
				      ('/editsubject', CreateEditSubject),
				      ('/viewsubject', ViewSubject),
				      ('/deletequestion', DeleteQuestion),
				      ('/deletesubject', DeleteSubject),
				      ('/changepublished', ChangePublished),
				      ('/pickquestiontopic', PickQuestionTopic),
				      ('/pickquiztopic', PickQuizTopic),
				      ('/answerquestion', AnswerQuestion),
				      ('/rating', Rating),
				      ('/viewquestion', ViewQuestion),
				      ('/editquestion', CreateEditQuestion),
				      ('/addquestion', CreateEditQuestion),
                                      ('/sign', Guestbook)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
