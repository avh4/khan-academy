from flask import current_app

def api_error_response(e):
    return current_app.response_class("API error. %s" % e.message, status=500)

