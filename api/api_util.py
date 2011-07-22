from flask import current_app
import logging

def api_error_response(e):
    logging.error("API error: %s" % e)
    return current_app.response_class("API error. %s" % e.message, status=500)

