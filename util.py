import urllib
import copy
from google.appengine.api import users

import facebook_util

topics_list = []
topics_list.append('Arithmetic')
topics_list.append('Chemistry')
topics_list.append('Developmental Math')
topics_list.append('Pre-algebra')
topics_list.append('MA Tests for Education Licensure (MTEL) -Pre-Alg')
topics_list.append('Geometry')
topics_list.append('California Standards Test: Geometry')
topics_list.append('Current Economics')
topics_list.append('Banking and Money')
topics_list.append('Venture Capital and Capital Markets')
topics_list.append('Finance')
topics_list.append('Credit Crisis')
topics_list.append('Currency')
topics_list.append('Valuation and Investing')
topics_list.append('Geithner Plan')
topics_list.append('Algebra')
topics_list.append('Algebra I Worked Examples')
topics_list.append('ck12.org Algebra 1 Examples')
topics_list.append('California Standards Test: Algebra I')
topics_list.append('California Standards Test: Algebra II')
topics_list.append('Brain Teasers')
topics_list.append('Biology')
topics_list.append('Trigonometry')
topics_list.append('Precalculus')
topics_list.append('Statistics')
topics_list.append('Probability')
topics_list.append('Calculus')
topics_list.append('Differential Equations')
topics_list.append('Khan Academy-Related Talks and Interviews')
topics_list.append('History')
topics_list.append('Organic Chemistry')
topics_list.append('Linear Algebra')
topics_list.append('Physics')
topics_list.append('Paulson Bailout')
topics_list.append('CAHSEE Example Problems')
topics_list.append('Cosmology and Astronomy')
topics_list.sort()

all_topics_list = copy.copy(topics_list)
all_topics_list.append('SAT Preparation')        
all_topics_list.append('GMAT: Problem Solving')
all_topics_list.append('GMAT Data Sufficiency')        
all_topics_list.append('Singapore Math')        
all_topics_list.sort()  


"""Returns users.get_current_user() if not None, or a faked User based on the
user's Facebook account if the user has one, or None.
"""
def get_current_user():

    appengine_user = users.get_current_user()

    if appengine_user is not None:
        return appengine_user

    facebook_user = facebook_util.get_current_facebook_user()

    if facebook_user is not None:
        return facebook_user   

    return None

def get_nickname_for(user):
    if facebook_util.is_facebook_email(user.email()):
        return facebook_util.get_facebook_nickname(user)
    else:
        return user.nickname()

def create_login_url(dest_url):
    return "/login?continue=%s" % urllib.quote(dest_url)
