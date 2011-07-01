import models
from badges.models_badges import UserBadge
from badges.badges import Badge
import logging
from google.appengine.api import taskqueue
import request_handler
from google.appengine.api import users
import util

def clone_problemlog(userData, newUser):
    query = models.ProblemLog.all()
    query.filter('user =', userData.user)
    for problem_logs in query:
        problem_logs = clone_entity(problem_logs, True, user=newUser)
    logging.info("Completed ProblemLog transfer for NewUser:%s", newUser.email())

def clone_videolog(userData, newUser):
    query = models.VideoLog.all()
    query.filter('user =', userData.user)
    for video_logs in query:
        video_logs = clone_entity(video_logs, True, user=newUser)
    taskqueue.add(url='/transferaccount', name='ProblemLog', 
        queue_name='trythrice',params={'current_user': newUser, 'phantom_user': userData.user, 'data': "ProblemLog"})
    logging.info("Completed VideoLog transfer for NewUser:%s", newUser.email())    
        
def clone_uservideo(userData, newUser):
    query = models.UserVideo.all()
    query.filter('user =', userData.user)
    for user_videos in query:
        tkey = user_videos.get_key_name(user_videos.video,newUser)
        user_videos = clone_entity(user_videos, True, key_name=tkey, user=newUser)
    taskqueue.add(url='/transferaccount', name='UserBadge', 
        params={'current_user': newUser, 'phantom_user': userData.user, 'data': "UserBadge"})
    logging.info("Completed UserVideo transfer for NewUser:%s", newUser.email())

def clone_userbadge(userData, newUser):
    query = UserBadge.all()
    query.filter('user =', userData.user)
    for user_badges in query:
        name_with_context = "["+user_badges.target_context_name+"]" or ""
        key_name = newUser.email() + ":" + user_badges.badge_name + name_with_context
        user_badges = clone_entity(user_badges, True, key_name=key_name, user=newUser)
    taskqueue.add(url='/transferaccount', name='UserPlaylist', 
        params={'current_user': newUser, 'phantom_user': userData.user, 'data': "UserPlaylist"})
    logging.info("Completed UserBadge transfer for NewUser:%s", newUser.email())

def clone_userplaylist(userData, newUser):
    query = models.UserPlaylist.all()
    query.filter('user =', userData.user)
    for playlists in query:
        key_name = models.UserPlaylist.get_key_name(playlists.playlist, newUser)
        playlists = clone_entity(playlists, True, key_name=key_name, user=newUser)
    taskqueue.add(url='/transferaccount', name='VideoLog', 
        queue_name='trythrice',params={'current_user': newUser, 'phantom_user': userData.user, 'data': "VideoLog"})
    logging.info("Completed UserPlaylist transfer for NewUser:%s", newUser.email())
        
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

class TransferHandler(request_handler.RequestHandler):
    def get(self):       
        #Current user is the non phantom user 
        current_user = util.get_current_user()
        phantom_user = util.get_phantom_user_from_cookies()
        cont = self.request_string('continue', default = "/")
        
        if phantom_user == None:
            self.redirect("/transferaccount?continue=%s" % cont)
            return
        
        phantom_data = models.UserData.get_for(phantom_user) 
        current_data = models.UserData.get_for(current_user)
        
        if current_data.points != 0:
            self.redirect("/transferaccount?continue=%s" % cont)
            return
            
        logging.info("Transferring data from Phanntom: %s to NewUser: %s",phantom_user.email() , current_user.email())
        #Create UserMigration Model
        models.UserMigration.get_or_insert_for(phantom_user,current_user)
        #Clone UserData
        key = "user_email_key_%s" % current_user.email()
        c = clone_entity(phantom_data, True, key_name=key, user=current_user)
        logging.info("UserData copied for %s", current_user.email())
        #Clone UserExercise
        query = models.UserExercise.all()
        query.filter('user =', phantom_user)
        for c in query:
            c = clone_entity(c, True, key_name=c.exercise, user=current_user)
        logging.info("UserExercise copied for %s", current_user.email())
        self.delete_cookie('ureg_id')
        taskqueue.add(url='/transferaccount', name='UserVideo', 
                params={'current_user': current_user, 'phantom_user': phantom_user, 'data': "UserVideo"})    
        self.redirect("/transferaccount?continue=%s" % cont)


class Clone(request_handler.RequestHandler):
    def get(self):
        title = "Please wait while we copy your data to your new account."
        message_html = "We're in the process of copying over all of the progress you've made. Your may access your account once the transfer is complete."
        sub_message_html = "This process can take a long time, thank you for your patience."
        cont = self.request_string('continue', default = "/")
        self.render_template('phantom_users/transfer.html',
            {'title': title, 'message_html':message_html,"sub_message_html":sub_message_html, "dest_url":cont})
            
    def post(self):
        datatype = self.request.get('data')
        phantom_user = self.request.get('phantom_user')
        current_user = self.request.get('current_user')
        phantom_data = models.UserData.get_for(users.User(phantom_user))
        current_user = users.User(current_user)
        logging.info("Kicking off Task:%s for NewUser:%s", datatype, current_user.email())
        
        if datatype == "ProblemLog":
            clone_problemlog(phantom_data, current_user)
        elif datatype == "VideoLog":
            clone_videolog(phantom_data, current_user)
        elif datatype == "UserVideo":
            clone_uservideo(phantom_data, current_user)
        elif datatype == "UserBadge":
            clone_userbadge(phantom_data, current_user)
        elif datatype == "UserPlaylist":
            clone_userplaylist(phantom_data, current_user)