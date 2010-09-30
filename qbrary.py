#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from google.appengine.ext.webapp import template
import random
import logging

import cgi

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

import app

# Note: this class adapted from: http://github.com/Arachnid/aetycoon/blob/master/__init__.py#L496
class ChoiceProperty(db.IntegerProperty):
  """A property for efficiently storing choices made from a finite set.

  This works by mapping each choice to an integer.  The choices must be hashable
  (so that they can be efficiently mapped back to their corresponding index).

  Example usage:

  >>> class ChoiceModel(db.Model):
  ...   a_choice = ChoiceProperty(enumerate(['red', 'green', 'blue']))
  ...   b_choice = ChoiceProperty([(0,None), (1,'alpha'), (4,'beta')])

  You interact with choice properties using the choice values:

  >>> model = ChoiceModel(a_choice='green')
  >>> model.a_choice
  'green'
  >>> model.b_choice == None
  True
  >>> model.b_choice = 'beta'
  >>> model.b_choice
  'beta'
  >>> model.put() # doctest: +ELLIPSIS
  datastore_types.Key.from_path(u'ChoiceModel', ...)

  >>> model2 = ChoiceModel.all().get()
  >>> model2.a_choice
  'green'
  >>> model.b_choice
  'beta'

  To get the int representation of a choice, you may use either access the
  choice's corresponding attribute or use the c2i method:
  >>> green = ChoiceModel.a_choice.GREEN
  >>> none = ChoiceModel.b_choice.c2i(None)
  >>> (green == 1) and (none == 0)
  True

  The int representation of a choice is needed to filter on a choice property:
  >>> ChoiceModel.gql("WHERE a_choice = :1", green).count()
  1
  """
  def __init__(self, choices, make_choice_attrs=True, *args, **kwargs):
    """Constructor.

    Args:
      choices: A non-empty list of 2-tuples of the form (id, choice). id must be
        the int to store in the database.  choice may be any hashable value.
      make_choice_attrs: If True, the uppercase version of each string choice is
        set as an attribute whose value is the choice's int representation.
    """
    super(ChoiceProperty, self).__init__(*args, **kwargs)
    self.index_to_choice = dict(choices)
    self.choice_to_index = dict((c,i) for i,c in self.index_to_choice.iteritems())
    if make_choice_attrs:
      for i,c in self.index_to_choice.iteritems():
        if isinstance(c, basestring):
          setattr(self, c.upper(), i)

  def get_choices(self):
    """Gets a list of values which may be assigned to this property."""
    return self.choice_to_index.keys()

  def c2i(self, choice):
    """Converts a choice to its datastore representation."""
    return self.choice_to_index[choice]

  def __get__(self, model_instance, model_class):
    if model_instance is None:
      return self
    index = super(ChoiceProperty, self).__get__(model_instance, model_class)
    return self.index_to_choice[index]

  def __set__(self, model_instance, value):
      if (value == None):
          return

      try:
          index = self.c2i(value)
      except KeyError:
          raise db.BadValueError('Property %s must be one of the allowed choices: %s' %
                                 (self.name, self.get_choices()))
      super(ChoiceProperty, self).__set__(model_instance, index)

  def get_value_for_datastore(self, model_instance):
    # just use the underlying value from the parent
    return super(ChoiceProperty, self).__get__(model_instance, model_instance.__class__)

  def make_value_from_datastore(self, value):
    if value is None:
      return None
    return self.index_to_choice[value]


class Greeting(db.Model):

    author = db.UserProperty()
    content = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)


class Subject(db.Model):

    author = db.UserProperty()
    name = db.StringProperty()
    parent_subject = db.SelfReferenceProperty()
    index = db.IntegerProperty()  # to order a child subject within a parent subject


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
    not_completed = db.BooleanProperty()  # Test's if the user actually didn't completed the creation process
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
    importance_width = db.IntegerProperty()  # used for the pixel width of the actual stars
    difficulty_rating = db.RatingProperty()
    difficulty_width = db.IntegerProperty()  # used for the pixel width of the actual stars
    quality_rating = db.RatingProperty()
    quality_width = db.IntegerProperty()  # used for the pixel width of the actual stars
    flag = ChoiceProperty(enumerate(['inappropriate', 'spam', 'miscategorized']))


class QuestionAnswerSession(db.Model):

    answerer = db.UserProperty()
    question = db.ReferenceProperty(Question)
    page_loaded_timestamp = db.DateTimeProperty(auto_now_add=True)  # set auto_now_add to True so that it's auto set on insert
    correct_on_first_attempt = db.BooleanProperty()
    total_attempts = db.IntegerProperty()
    choice_0 = db.IntegerProperty()
    choice_1 = db.IntegerProperty()
    choice_2 = db.IntegerProperty()
    choice_3 = db.IntegerProperty()
    choice_4 = db.IntegerProperty()


class QuestionAnswerSessionAttempt(db.Model):

    session = db.ReferenceProperty(QuestionAnswerSession)
    answer_chosen_timestamp = db.DateTimeProperty(auto_now_add=True)  # set auto_now_add to True so that it's auto set on insert
    answer_chosen_index = db.IntegerProperty()
    was_correct = db.BooleanProperty()


#class QuestionAnswerSessionActionTypes(db.Model):
#    type = db.StringProperty()


class QuestionAnswerSessionAction(db.Model):

    session = db.ReferenceProperty(QuestionAnswerSession)
#    action = db.ReferenceProperty(QuestionAnswerSessionActionTypes)
    action = ChoiceProperty(enumerate(['hint_button_clicked', 'explain_button_clicked', 'next_button_clicked']))
    timestamp = db.DateTimeProperty(auto_now_add=True)  # set auto_now_add to True so that it's auto set on insert


class AnswerLog(db.Model):

    answer_author = db.UserProperty()
    question = db.ReferenceProperty(Question)
    tries = db.IntegerProperty()
    date = db.DateTimeProperty(auto_now_add=True)


def breadcrumb(subj):
    b = []
    parent_subject = subj.parent_subject
    while parent_subject:
        if parent_subject.parent_subject:  # don't want to add the root
            b.append(parent_subject)
        parent_subject = parent_subject.parent_subject
    b.reverse()
    return b


def subtopics(subj):
    return Subject.gql('WHERE parent_subject = :1 ORDER BY index', subj)


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
    output = '<B>' + subject.name + '</B>'

    s_topics = subtopics(subject)
    if s_topics.count() < 1:
        output = output + " | <A href='/addquestion?subject_key=" + subject.key().__str__() + "'>Add Question</a><br>"
    else:
        output = output + '<UL>'
        for topic in s_topics:
            output = output + '<LI>' + htmlChildren(topic) + '</LI>'
        output = output + '</UL>'

    return output


def str_to_bool(str):
    return str == 'True' or str == 'true'


def pickQuestionTopicHTML(subject):
    output = '<B>' + subject.name + '</B>'

    s_topics = subtopics(subject)
    if s_topics.count() < 1:
        output = "<A href='/addquestion?subject_key=" + subject.key().__str__() + "'><B>" + subject.name + '</B></a><br>'
    else:
        output = output + '<UL>'
        for topic in s_topics:
            output = output + '<LI>' + pickQuestionTopicHTML(topic) + '</LI>'
        output = output + '</UL>'

    return output


def pickQuizTopicHTML(subject):
    output = "<A href='/answerquestion?subject_key=" + subject.key().__str__() + "'><B>" + subject.name + '</B></a><br>'

    s_topics = subtopics(subject)
    if s_topics.count() > 0:
        output = output + '<UL>'
        for topic in s_topics:
            output = output + '<LI>' + pickQuizTopicHTML(topic) + '</LI>'
        output = output + '</UL>'

    return output


# Returns a list of the most granular subtopics within a topic


def getBottomLevelChildren(subj):
    output = []
    s_topics = subtopics(subj)
    if s_topics.count() < 1:
        output = [subj]
    else:
        for topic in s_topics:
            output.extend(getBottomLevelChildren(topic))
    return output

"""
class InitQbrary(app.RequestHandler):

    def get(self):
        action_types = ['hint_button_clicked', 'explain_button_clicked', 'next_button_clicked']
        for action_type in action_types:
            new_action = QuestionAnswerSessionActionTypes()
            new_action.type = action_type
            new_action.put()
"""

class DeleteSubject(app.RequestHandler):

    def get(self):
        user = app.get_current_user()
        subject_key = self.request.get('subject_key')
        subject = db.get(subject_key)
        redirect_url = self.request.get('redirect')
        logging.error("current user = " + str(user))

        if user:
            if user == subject.author:
                subject = db.get(subject_key)
                self.delete_subject(subject)

            self.redirect(redirect_url)
        else:
            self.redirect(app.create_login_url(self.request.uri))

    def delete_subject(self, subject):
        logging.error("delete_subject subject_key = " + str(subject.key()))

        child_subjects = Subject.gql('WHERE parent_subject=:1', subject)
        for child_subject in child_subjects:
            self.delete_subject(child_subject)

        self.delete_questions_for_subject(subject)
        subject.delete()        

    def delete_questions_for_subject(self, subject):
        questions = Question.gql('WHERE parent_subject=:1', subject)
        for cur_question in questions:
            self.delete_question_dependencies_for_question(cur_question)
            cur_question.delete()
            
    def delete_question_dependecies_for_question(self, question):
        qa = QuestionAnswerer.gql('WHERE question=:1', question)
        for cur_qa in qa:
            cur_qa.delete()

        qa_sessions = QuestionAnswerSession.gql('WHERE question=:1', question)
        for cur_qa_session in qa_sessions:
            self.delete_session_dependencies_for_session(cur_qa_session)
            cur_qa_session.delete()

    def delete_session_dependencies_for_session(self, session):
        qas_attempts = QuestionAnswerSessionAttempt.gql('WHERE session=:1', session)
        for cur_qas_att in qas_attempts:
            cur_qas_att.delete()

        qas_actions = QuestionAnswerSessionAction.gql('WHERE session=:1', session)
        for cur_qas_action in qas_actions:
            cur_qas_action.delete()


class DeleteQuestion(app.RequestHandler):

    def get(self):
        user = app.get_current_user()
        question_key = self.request.get('question_key')
        question = db.get(question_key)
        redirect_url = self.request.get('redirect')
        if user:
            if user == question.author:
                question.delete()
            self.redirect(redirect_url)
        else:
            self.redirect(app.create_login_url(self.request.uri))


class ChangePublished(app.RequestHandler):

    def get(self):
        user = app.get_current_user()
        question_key = self.request.get('question_key')
        question = db.get(question_key)
        redirect_url = self.request.get('redirect')
        if user:
            if user == question.author:
                if question.published:
                    question.published = None
                else:
                    question.published = True
                question.put()
#            self.redirect(redirect_url)
            self.redirect('/qbrary')
        else:
            self.redirect(app.create_login_url(self.request.uri))


class IntroPage(app.RequestHandler):

    def get(self):
        # note: don't require login to view the intro page
        subs = Subject.gql('WHERE parent_subject=:1', None)

        # We need at least the root subject

        if subs.count() < 1:
            path = os.path.join(os.path.dirname(__file__), 'qbraryempty.html')
            self.response.out.write(template.render(path, None))
        else:
            root = subs[0]

            # select all of the children of the root subject to
            subjects = Subject.gql('WHERE parent_subject = :1', root)
    
            # select all of the questions that the user has created
            if subjects.count() < 1:
                path = os.path.join(os.path.dirname(__file__), 'qbraryempty.html')
                self.response.out.write(template.render(path, None))
            else:
                subject = subjects[0]
                template_values = {
                    'subject': subject,
                    }
        
                path = os.path.join(os.path.dirname(__file__), 'qbraryintro.html')
                self.response.out.write(template.render(path, template_values))
        

class ManageQuestions(app.RequestHandler):

    def get(self):

        user = app.get_current_user()
        if user:

            # Do a SQL query to select the root subject (it has no parent)

            subs = Subject.gql('WHERE parent_subject=:1', None)

            # We need at least the root subject

            if subs.count() < 1:
                root = Subject()
                root.author = user
                root.name = 'root'
                root.put()
            else:
                root = subs[0]

            # select all of the children of the root subject to

            subjects = Subject.gql('WHERE parent_subject = :1', root)

            # select all of the questions that the user has created

            published = Question.gql('WHERE author = :1 and published = :2 and not_completed = :3', user, True, False)
            notpublished = Question.gql('WHERE author = :1 and published = :2 and not_completed = :3', user, None, False)
            greeting = 'user: %s [<a href="%s">sign out</a>]' % (user.nickname(), users.create_logout_url('/'))

            template_values = {
                'subjects': subjects,
                'greeting': greeting,
                'published': published,
                'notpublished': notpublished,
                'current_url': self.request.uri,
                'user': user,
                }

            path = os.path.join(os.path.dirname(__file__), 'myprofile.html')
            self.response.out.write(template.render(path, template_values))
        else:

            self.redirect(app.create_login_url(self.request.uri))


class CreateEditSubject(app.RequestHandler):

    def get(self):
        if not users.is_current_user_admin():
            self.redirect(app.create_login_url(self.request.uri))
            return

        user = app.get_current_user()

        # This if/then clause just makes sure that the user is logged in

        if user:
            subject_key = self.request.get('subject_key')
            subject_name = self.request.get('subject_name')  # Get this if editing name of subject
            child_name = self.request.get('child_name')  # Get this if adding child to subject

            # Get the subject key if we are editing its name or adding a child
            # I think this will always be the case so we may want to get rid of the if/then clause and
            # just do the if part

            if subject_key:
                subject = db.get(subject_key)
            else:
                subject = Subject(author=user)

            st = subtopics(subject)
            next_index = st.count() + 1

            # This is the case that someone has created or changed a subject's name (forwards back to profile page)
            # This subject has no parent and no index

            if subject_name:
                subject.name = subject_name
                subject.put()
                self.redirect('/qbrary')
            else:

                # This is the case the someone is adding a subtopic to this subject

                if child_name:
                    child_subject = Subject()
                    child_subject.author = user
                    child_subject.name = child_name
                    child_subject.parent_subject = subject
                    child_subject.index = next_index
                    child_subject.put()
                    st = subtopics(subject)

                    # subtopics = Subject.gql("WHERE parent_subject = :1 ORDER BY index", subject)

                bc = breadcrumb(subject)
                html_tree = htmlChildren(subject)

                root = Subject.gql('WHERE parent_subject=:1', None).get()
                subjects = Subject.gql('WHERE parent_subject = :1', root)
                greeting = 'user: %s [<a href="%s">sign out</a>]' % (user.nickname(), users.create_logout_url('/'))

                template_values = {
                    'subject': subject,
                    'subjects': subjects,
                    'greeting': greeting,
                    'subtopics': st,
                    'tree': html_tree,
                    'breadcrumb': bc,
                    'redirect_url': self.request.uri,
                    }
                path = os.path.join(os.path.dirname(__file__), 'editsubject.html')
                self.response.out.write(template.render(path, template_values))
        else:

            self.redirect(app.create_login_url(self.request.uri))


class ViewSubject(app.RequestHandler):

    def get(self):
        user = app.get_current_user()
        if user:
            subject_key = self.request.get('subject_key')
            if subject_key:
                subject = db.get(subject_key)
                html_tree = htmlChildren(subject)
                template_values = {'subject': subject, 'tree': html_tree}
                path = os.path.join(os.path.dirname(__file__), 'viewsubject.html')
                self.response.out.write(template.render(path, template_values))
        else:
            self.redirect(app.create_login_url(self.request.uri))


class Rating(app.RequestHandler):

    def get(self):
        user = app.get_current_user()
        if user:
            user_question_key = self.request.get('key')
            difrating = self.request.get('difrating')
            qualrating = self.request.get('qualrating')
            imprating = self.request.get('imprating')
            if user_question_key:
                user_question = db.get(user_question_key)

                # if user==user_question.answerer:

                if difrating:
                    difrating = int(difrating)
                    user_question.difficulty_rating = difrating
                    user_question.difficulty_width = difrating * 20
                    user_question.put()
                    rating_type = 'difficulty'
                    rating = difrating
                    rating_width = difrating * 20
                if imprating:
                    imprating = int(imprating)
                    user_question.importance_rating = imprating
                    user_question.importance_width = imprating * 20
                    user_question.put()
                    rating_type = 'importance'
                    rating = imprating
                    rating_width = imprating * 20
                if qualrating:
                    qualrating = int(qualrating)
                    user_question.quality_rating = qualrating
                    user_question.quality_width = qualrating * 20
                    user_question.put()
                    rating_type = 'quality'
                    rating = qualrating
                    rating_width = qualrating * 20

                template_values = {
                    'user_question': user_question,
                    'rating': rating,
                    'rating_width': rating_width,
                    'rating_type': rating_type,
                    }
                path = os.path.join(os.path.dirname(__file__), 'rating.html')
                self.response.out.write(template.render(path, template_values))


class PreviewQuestion(app.RequestHandler):
    def get(self):
        user = app.get_current_user()
        if user:
            question_key = self.request.get('question_key')
            self.redirect('/answerquestion?question_key=' + question_key + '&preview_mode=True')
        else:
            self.redirect(app.create_login_url(self.request.uri))


class AnswerQuestion(app.RequestHandler):

    def get(self):
        user = app.get_current_user()
        if user:
            subject_key = self.request.get('subject_key')
            question_key = self.request.get('question_key')
            preview_mode = self.request.get('preview_mode')
            question = None
            subject = None

            root = Subject.gql('WHERE parent_subject=:1', None).get()
            subjects = Subject.gql('WHERE parent_subject = :1', root)
            greeting = 'user: %s [<a href="%s">sign out</a>]' % (user.nickname(), users.create_logout_url('/'))

            if subject_key:
                # get all questions that are in some subtopic of given subject
                subject = db.get(subject_key)
                children = getBottomLevelChildren(subject)
                questions = []
                for subj in children:
                    questions.extend(Question.gql('WHERE subject=:1 and published =:2', subj, True))
                    
                # pick a random question 
                if len(questions) > 0:
                    question = random.choice(questions)
                    
            elif question_key:
                # lookup question with given key (for preview functionality)
                question = db.get(question_key)
                subject = question.subject

            if question:
                untested_warning = QuestionAnswerer.gql('WHERE question=:1', question).count() < 5  # TODO: clean this up

                answerer_question = QuestionAnswerer.gql('WHERE answerer=:1 and question=:2', user, question).get()

                # check if current user has answered the question before
                # create new QuestionAnswerer entry if they haven't

                if not answerer_question:
                    answerer_question = QuestionAnswerer()
                    answerer_question.answerer = user
                    answerer_question.question = question
                    answerer_question.difficulty_rating = 0
                    answerer_question.quality_rating = 0
                    answerer_question.importance_rating = 0
                    answerer_question.difficulty_width = 0
                    answerer_question.quality_width = 0
                    answerer_question.importance_width = 0
                    answerer_question.put()
                # need to randomly take out 4 of the incorrect choices

                correct_index = random.randint(0, 4)
                all_incorrect_indices = [1, 2, 3, 4, 5]
                question_ordering = random.sample(all_incorrect_indices, 4)
                question_ordering.insert(correct_index, 0)

                # by this point, question_ordering is an array with 5 indices, and holds 0 (correct answer) along with 4 of (1..5) in a random order, eg [4,0,3,1,2]

                choices = []
                for question_index in question_ordering:
                    if question_index == 0:
                        choices.append(question.correct_choice_text)
                    if question_index == 1:
                        choices.append(question.incorrect_1)
                    if question_index == 2:
                        choices.append(question.incorrect_2)
                    if question_index == 3:
                        choices.append(question.incorrect_3)
                    if question_index == 4:
                        choices.append(question.incorrect_4)
                    if question_index == 5:
                        choices.append(question.incorrect_5)

                # create an answer session for this question
                # todo: need to set the choice_* fields

                qa_session = QuestionAnswerSession()
                qa_session.answerer = user
                qa_session.question = question
                qa_session.total_attempts = 0
                qa_session.choice_0 = question_ordering[0]
                qa_session.choice_1 = question_ordering[1]
                qa_session.choice_2 = question_ordering[2]
                qa_session.choice_3 = question_ordering[3]
                qa_session.choice_4 = question_ordering[4]
                qa_session.put()
                
                publish_button_text = 'Publish Question'
                if question.published == True:
                    publish_button_text = 'Unpublish Question'
                
                template_values = {
                    'subject': subject,
                    'subjects': subjects,
                    'greeting': greeting,
                    'user_question': answerer_question,
                    'correct_index': correct_index,
                    'choice0': choices[0],
                    'choice1': choices[1],
                    'choice2': choices[2],
                    'choice3': choices[3],
                    'choice4': choices[4],
                    'question': question,
                    'session_key': str(qa_session.key()),
                    'untested_warning': untested_warning,
                    'preview_mode': preview_mode,
                    'question_key': question_key,
                    'publish_button_text' : publish_button_text
                    }

                path = os.path.join(os.path.dirname(__file__), 'answerquestion.html')
                self.response.out.write(template.render(path, template_values))
            else:
                template_values = {'subject': subject, 'subjects': subjects, 'greeting': greeting}
                path = os.path.join(os.path.dirname(__file__), 'noquestion.html')
                self.response.out.write(template.render(path, template_values))
        else:
            self.redirect(app.create_login_url(self.request.uri))


class ViewQuestion(app.RequestHandler):

    def get(self):
        user = app.get_current_user()

        # This if/then clause just makes sure that the user is logged in

        if user:
            question_key = self.request.get('question_key')
            if question_key:
                question = db.get(question_key)
                bc = breadcrumb(question.subject)
                root = Subject.gql('WHERE parent_subject=:1', None).get()
                subjects = Subject.gql('WHERE parent_subject = :1', root)
                greeting = 'user: %s [<a href="%s">sign out</a>]' % (user.nickname(), users.create_logout_url('/'))

                template_values = {
                    'question': question,
                    'subjects': subjects,
                    'greeting': greeting,
                    'current_url': self.request.uri,
                    'breadcrumb': bc,
                    }
                path = os.path.join(os.path.dirname(__file__), 'viewquestion.html')
                self.response.out.write(template.render(path, template_values))
        else:
            self.redirect(app.create_login_url(self.request.uri))


class ViewAuthors(app.RequestHandler):
    
    def get(self):
        user = app.get_current_user()
        if user:
            questions = Question.gql('')
            author_questions_dict = dict()
            for question in questions:
                if question.author.nickname() in author_questions_dict:
                    author_questions_dict[question.author.nickname()].append(question.question_text)
                else:
                    author_questions_dict[question.author.nickname()] = [question.question_text]

            template_values = {
                'author_questions_dict': author_questions_dict,
                'greeting': "boo",
                'current_url': self.request.uri
                }
            path = os.path.join(os.path.dirname(__file__), 'viewauthors.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect(app.create_login_url(self.request.uri))
        

class PickQuestionTopic(app.RequestHandler):

    def get(self):
        user = app.get_current_user()
        if user:
            root = Subject.gql('WHERE parent_subject=:1', None).get()
            subjects = Subject.gql('WHERE parent_subject = :1', root)
            greeting = 'user: %s [<a href="%s">sign out</a>]' % (user.nickname(), users.create_logout_url('/'))

            subject_key = self.request.get('subject_key')
            if subject_key:
                subject = db.get(subject_key)
                html_tree = pickQuestionTopicHTML(subject)
                template_values = {
                    'subject': subject,
                    'subjects': subjects,
                    'greeting': greeting,
                    'tree': html_tree,
                    }
                path = os.path.join(os.path.dirname(__file__), 'pickquestiontopic.html')
                self.response.out.write(template.render(path, template_values))
        else:
            self.redirect(app.create_login_url(self.request.uri))


class PickQuizTopic(app.RequestHandler):

    def get(self):
        user = app.get_current_user()
        if user:
            subject_key = self.request.get('subject_key')
            if subject_key:
                subject = db.get(subject_key)
                root = Subject.gql('WHERE parent_subject=:1', None).get()
                subjects = Subject.gql('WHERE parent_subject = :1', root)
                greeting = 'user: %s [<a href="%s">sign out</a>]' % (user.nickname(), users.create_logout_url('/'))

                html_tree = pickQuizTopicHTML(subject)
                template_values = {
                    'subject': subject,
                    'subjects': subjects,
                    'greeting': greeting,
                    'tree': html_tree,
                    }
                path = os.path.join(os.path.dirname(__file__), 'pickquiztopic.html')
                self.response.out.write(template.render(path, template_values))
        else:
            self.redirect(app.create_login_url(self.request.uri))


class SubjectManager(app.RequestHandler):

    def get(self):
        user = app.get_current_user()

        # This if/then clause just makes sure that the user is logged in

        if user:
            subs = Subject.gql('WHERE parent_subject=:1', None)

            # We need at least the root subject

            if subs.count() < 1:
                root = Subject()
                root.author = user
                root.name = 'root'
                root.put()
            else:
                root = subs[0]

            self.redirect('/editsubject?subject_key=' + root.key().__str__())
        else:
            self.redirect(app.create_login_url(self.request.uri))


class CreateEditQuestion(app.RequestHandler):

    def get(self):
        user = app.get_current_user()

        # This if/then clause just makes sure that the user is logged in

        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'

            # If we are creating a new question, we need the subject

            subject_key = self.request.get('subject_key')

            # If we are editing/updating a previously created question, we need to be passed the key

            question_key = self.request.get('question_key')

            # If question_text is set, then we have to update the question

            question_text = self.request.get('question_text')

            # if true, then update the question and forward to viewquestion

            if question_text:
                question = db.get(question_key)
                if question.author == user:  # This here to make sure that someone can't hack someone else's question
                    question.question_text = question_text
                    question.correct_choice_text = self.request.get('correct_choice_text')
                    question.incorrect_1 = self.request.get('incorrect_1')
                    question.incorrect_2 = self.request.get('incorrect_2')
                    question.incorrect_3 = self.request.get('incorrect_3')
                    question.incorrect_4 = self.request.get('incorrect_4')
                    question.incorrect_5 = self.request.get('incorrect_5')
                    question.answer_text = self.request.get('answer_text')
                    question.hint_text = self.request.get('hint_text')
                    question.not_completed = False
                    question.put()
                    self.redirect('/qbrary')

            # If we have a key, then we can retrieve the question; otherwise
            # need to create a new one

            if question_key:
                question = db.get(question_key)
                mode_text = 'Edit Question'
                button_text = 'Save Updates and Preview'
                message_text = ' '
            else:

                question = Question(author=user)
                question.not_completed = True
                question.subject = db.get(subject_key)
                question.question_text = ''
                question.correct_choice_text = ''
                question.incorrect_1 = ''
                question.incorrect_2 = ''
                question.incorrect_3 = ''
                question.incorrect_4 = ''
                question.incorrect_5 = ''
                question.answer_text = ''
                question.hint_text = ''
                question.put()
                mode_text = 'Add Question'
                button_text = 'Create Question and Preview'
                message_text = 'Step 2: Write the question...'

            bc = breadcrumb(question.subject)

            root = Subject.gql('WHERE parent_subject=:1', None).get()
            subjects = Subject.gql('WHERE parent_subject = :1', root)
            greeting = 'user: %s [<a href="%s">sign out</a>]' % (user.nickname(), users.create_logout_url('/'))

            template_values = {
                'question': question,
                'breadcrumb': bc,
                'message_text': message_text,
                'subjects': subjects,
                'greeting': greeting,
                'button_text': button_text,
                'mode_text': mode_text,
                }
            path = os.path.join(os.path.dirname(__file__), 'editquestion.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect(app.create_login_url(self.request.uri))
    #replicating the functionality described in "get" in "post".  Should clean this up in the future
    #but I just wanted it to be able to process longer fields (so they wouldn't have to be in the URL).
    def post(self):
    	user = app.get_current_user()

        # This if/then clause just makes sure that the user is logged in

        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'

            # If we are creating a new question, we need the subject

            subject_key = self.request.get('subject_key')

            # If we are editing/updating a previously created question, we need to be passed the key

            question_key = self.request.get('question_key')

            # If question_text is set, then we have to update the question

            question_text = self.request.get('question_text')

            # if true, then update the question and forward to viewquestion

            if question_text:
                question = db.get(question_key)
                if question.author == user:  # This here to make sure that someone can't hack someone else's question
                    question.question_text = question_text
                    question.correct_choice_text = self.request.get('correct_choice_text')
                    question.incorrect_1 = self.request.get('incorrect_1')
                    question.incorrect_2 = self.request.get('incorrect_2')
                    question.incorrect_3 = self.request.get('incorrect_3')
                    question.incorrect_4 = self.request.get('incorrect_4')
                    question.incorrect_5 = self.request.get('incorrect_5')
                    question.answer_text = self.request.get('answer_text')
                    question.hint_text = self.request.get('hint_text')
                    question.not_completed = False
                    new_question_key = question.put()
                    self.redirect('/previewquestion?question_key=' + str(new_question_key))

            # If we have a key, then we can retrieve the question; otherwise
            # need to create a new one

            if question_key:
                question = db.get(question_key)
                mode_text = 'Edit Question'
                button_text = 'Save Updates'
                message_text = ' '
            else:

                question = Question(author=user)
                question.not_completed = True
                question.subject = db.get(subject_key)
                question.question_text = ''
                question.correct_choice_text = ''
                question.incorrect_1 = ''
                question.incorrect_2 = ''
                question.incorrect_3 = ''
                question.incorrect_4 = ''
                question.incorrect_5 = ''
                question.answer_text = ''
                question.hint_text = ''
                question.put()
                mode_text = 'Add Question'
                button_text = 'Create Question'
                message_text = 'Step 2: Write the question...'

            bc = breadcrumb(question.subject)

            root = Subject.gql('WHERE parent_subject=:1', None).get()
            subjects = Subject.gql('WHERE parent_subject = :1', root)
            greeting = 'user: %s [<a href="%s">sign out</a>]' % (user.nickname(), users.create_logout_url('/'))

            template_values = {
                'question': question,
                'breadcrumb': bc,
                'message_text': message_text,
                'subjects': subjects,
                'greeting': greeting,
                'button_text': button_text,
                'mode_text': mode_text,
                }
            path = os.path.join(os.path.dirname(__file__), 'editquestion.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect(app.create_login_url(self.request.uri))


class CheckAnswer(app.RequestHandler):

    def post(self):
        answer_chosen_index = self.request.get('answer_chosen_index')
        session_key = self.request.get('session_key')
        was_correct = self.request.get('was_correct')

    # get the current question answer session

        qa_session = db.get(db.Key(session_key))

    # record a new question answer attempt for the current session

        qa_session_att = QuestionAnswerSessionAttempt()
        qa_session_att.session = qa_session
        qa_session_att.answer_chosen_index = int(answer_chosen_index)
        qa_session_att.was_correct = str_to_bool(was_correct)
        qa_session_att.put()

        self.response.out.write('Recorded attempt for session: ' + session_key)


class SessionAction(app.RequestHandler):

    def post(self):
        action_type = self.request.get('action_type')
        session_key = self.request.get('session_key')

        qa_session = db.get(db.Key(session_key))

        # record a new question answer action
        qa_session_action = QuestionAnswerSessionAction()
        qa_session_action.session = qa_session
        qa_session_action.action = action_type
        qa_session_action.put()

        self.response.out.write(action_type)


class FlagQuestion(app.RequestHandler):
    def post(self):
        question_answerer_key = self.request.get('question_answerer_key')
        flag_type = self.request.get('flag_type')
        
        question_answerer = db.get(question_answerer_key)
        question_answerer.flag = flag_type
        question_answerer.put()

        self.response.out.write(flag_type)


class Guestbook(app.RequestHandler):

    def post(self):
        greeting = Greeting()

        if app.get_current_user():
            greeting.author = app.get_current_user()

        greeting.content = self.request.get('content')
        greeting.put()
        self.redirect('/')


application = webapp.WSGIApplication([
    ('/', IntroPage),
    ('/managequestions', ManageQuestions),
    ('/subjectmanager', SubjectManager),
    ('/editsubject', CreateEditSubject),
    ('/viewsubject', ViewSubject),
    ('/deletequestion', DeleteQuestion),
    ('/deletesubject', DeleteSubject),
    ('/changepublished', ChangePublished),
    ('/pickquestiontopic', PickQuestionTopic),
    ('/pickquiztopic', PickQuizTopic),
    ('/answerquestion', AnswerQuestion),
    ('/previewquestion', PreviewQuestion),
    ('/rating', Rating),
    ('/viewquestion', ViewQuestion),
    ('/editquestion', CreateEditQuestion),
    ('/addquestion', CreateEditQuestion),
    ('/checkanswer', CheckAnswer),
    ('/sessionaction', SessionAction),
    ('/flagquestion', FlagQuestion),
    ('/viewauthors', ViewAuthors),
    ('/sign', Guestbook),
    ], debug=True)


def main():
    run_wsgi_app(application)


if __name__ == '__main__':
    main()
