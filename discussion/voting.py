
from privileges import Privileges
import models
import request_handler
import util

class VoteEntity(request_handler.RequestHandler):
    def post(self):
        # You have to be logged in to vote
        user = util.get_current_user()
        if not user:
            return

        user_data = models.UserData.get_for_current_user(user)

        vote_type = self.request_bool("vote_type", default=True)
        if vote_type == FeedbackVote.UP and not Privileges.can_up_vote(user):
            return
        elif vote_type == FeedbackVote.DOWN and not Privileges.can_down_vote(user):
            return

        key = self.request_string("entity_key", default="")
        if key:
            entity = db.get(key)
            if entity and entity.add_vote_by(vote_type, user):
                entity.put()


