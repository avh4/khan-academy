import util

class Privileges:

    UP_VOTE_THRESHOLD = 5000
    DOWN_VOTE_THRESHOLD = 20000

    @staticmethod
    def can_up_vote(user_data):
        return user_data.points >= Privileges.UP_VOTE_THRESHOLD
    
    @staticmethod
    def can_down_vote(user_data):
        return user_data.points >= Privileges.DOWN_VOTE_THRESHOLD

    @staticmethod
    def need_points_desc(points, verb):
        return "You need at least %s energy points to %s." % (util.thousands_separated_number(points), verb)
 
