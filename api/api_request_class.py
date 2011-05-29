
from api import api_app
from flask import Request

class ApiRequest(Request):

    # Patch up a flask request object to behave a little more like webapp.RequestHandler
    # for the sake of our 3rd party oauth_provider library
    def arguments(self):
        return self.values
    def get(self, key):
        return self.values.get(key)

api_app.request_class = ApiRequest
