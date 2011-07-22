# import the webapp module
from google.appengine.ext import webapp

register = webapp.template.create_template_register()

@register.simple_tag
def mailing_list_signup_form(list_id):
    return webapp.template.render("mailing_lists/signup_form.html", {
    	"list_id": list_id
    })
