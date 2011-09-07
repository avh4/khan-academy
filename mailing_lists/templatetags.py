import template_cached
register = template_cached.create_template_register()

@register.inclusion_tag("mailing_lists/signup_form.html")
def mailing_list_signup_form(list_id, action, teaser):
    return { "list_id": list_id, "action": action, "teaser": teaser }
