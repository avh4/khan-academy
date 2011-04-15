
class Privileges:

    UP_VOTE_THRESHOLD = 1000
    DOWN_VOTE_THRESHOLD = 10000

    @staticmethod
    def can_up_vote(user_data):
        return user_data.points >= UP_VOTE_THRESHOLD
    
    @staticmethod
    def can_down_vote(user_data):
        return user_data.points >= DOWN_VOTE_THRESHOLD
 
