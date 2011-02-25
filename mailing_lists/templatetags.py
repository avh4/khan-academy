# import the webapp module
from google.appengine.ext import webapp

register = webapp.template.create_template_register()

@register.inclusion_tag(("../mailing_lists/signup_form.html", "mailing_lists/signup_form.html"))
def mailing_list_signup_form(list_id):
    return {"list_id": list_id}

