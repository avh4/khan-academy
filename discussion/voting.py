from google.appengine.ext import db

from privileges import Privileges
from models import UserData
from models_discussion import FeedbackVote
import request_handler
import util

class VoteEntity(request_handler.RequestHandler):
    def post(self):
        # You have to be logged in to vote
        user = util.get_current_user()
        if not user:
            return

        user_data = UserData.get_for(user)

        if not user_data:
            return

        vote_type = self.request_int("vote_type", default=FeedbackVote.ABSTAIN)
        if vote_type == FeedbackVote.UP and not Privileges.can_up_vote(user_data):
            return
        elif vote_type == FeedbackVote.DOWN and not Privileges.can_down_vote(user_data):
            return

        key = self.request_string("entity_key", default="")
        if key:
            entity = db.get(key)
            if entity and entity.add_vote_by(vote_type, user):
                entity.put()

def add_vote_expando_properties(feedback, dict_votes):
    feedback.up_voted = False
    feedback.down_voted = False
    if feedback.key() in dict_votes:
        vote = dict_votes[feedback.key()]
        feedback.up_voted = vote.is_up()
        feedback.down_voted = vote.is_down()
