import models
from badges.models_badges import UserBadge
from badges.badges import Badge
import logging
from google.appengine.ext import webapp
import request_handler
from google.appengine.api import users

def clone_userdata(userData, newUser):
    #Clone UserData
    c = clone_entity(userData, True, key_name='user_email_key_'+newUser.email(), user=newUser)

def clone_userexercise(userData, newUser):
    #Clone UserExercise
    query = models.UserExercise.all()
    query.filter('user =', userData.user)
    for b in query:
        b = clone_entity(b, True, key_name=b.get_key_for_user(newUser), user=newUser)

def clone_problemlog(userData, newUser):
    #Clone ProblemLog
    query = models.ProblemLog.all()
    query.filter('user =', userData.user)
    for b in query:
        b = clone_entity(b, True, user=newUser)

def clone_videolog(userData, newUser):
    #Clone VideoLog
    query = models.VideoLog.all()
    query.filter('user =', userData.user)
    for b in query:
        b = clone_entity(b, True, user=newUser)

def clone_uservideo(userData, newUser):
    #Clone UserVideo
    query = models.UserVideo.all()
    query.filter('user =', userData.user)
    for b in query:
        tkey = b.get_key_name(b.video,newUser)
        b = clone_entity(b, True, key_name=tkey, user=newUser)

def clone_userbadge(userData, newUser):
    #Clone UserBadge
    query = UserBadge.all()
    query.filter('user =', userData.user)
    for b in query:
        name_with_context = "["+b.target_context_name+"]" or ""
        key_name = newUser.email() + ":" + b.badge_name + name_with_context
        b = clone_entity(b, True, key_name=key_name, user=newUser)
        

def clone_entity(e, store, **extra_args):
    """Clones an entity, adding or overriding constructor attributes.
    The cloned entity will have exactly the same property values as the original
    entity, except where overridden. By default it will have no parent entity or
    key name, unless supplied.

    Args:
    e: The entity to clone
    extra_args: Keyword arguments to override from the cloned entity and pass
    to the constructor.
    Returns:
    cloned, possibly modified, copy of entity e.
    """
    klass = e.__class__
    props = dict((k, v.__get__(e, klass)) for k, v in klass.properties().iteritems())
    props.update(extra_args)
    if store:
        klass(**props).put()
    return klass(**props)


class Clone(request_handler.RequestHandler):
    def get(self):
        title = "Please wait while we copy your data to your new account."
        message_html = "We're in the process of copying over all of the progress you've made. Your may access your account once the transfer is complete."
        sub_message_html = "This process can take a long time, thank you for your patience."
        self.render_template('phantom_users/transfer.html',
                                                {'title': title, 'message_html':message_html,"sub_message_html":sub_message_html})
    
    def post(self):
        datatype = self.request.get('data')
        # userData = self.request.get('userData') 
        # newUser = self.request.get('newUser')
        userData = models.UserData.get_for_current_user()
        newUser = users.User("Test@test.com")
        # logging.critical(datatype)
        # logging.critical(userData)
        # logging.critical(newUser)
        
        
        if datatype == "UserData":
            clone_userdata(userData, newUser)
        elif datatype == "UserExercise":
            clone_userexercise(userData, newUser)
        elif datatype == "ProblemLog":
            clone_problemlog(userData, newUser)
        elif datatype == "VideoLog":
            clone_videolog(userData, newUser)
        elif datatype == "UserVideo":
            clone_uservideo(userData, newUser)
        elif datatype == "UserBadge":
            clone_userbadge(userData, newUser)
        
        #user = util.get_current_user()
       