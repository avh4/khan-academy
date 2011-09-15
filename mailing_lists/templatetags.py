import os

from google.appengine.ext.webapp import template

import template_cached
register = template_cached.create_template_register()

@register.simple_tag
def mailing_list_signup_form(list_id, action, teaser):
    template_context = { "list_id": list_id, "action": action, "teaser": teaser }

    path = os.path.join(os.path.dirname(__file__), "signup_form.html")
    return template.render(path, template_context)
