
from api import api_app

@api_app.route("/api/v1/hello")
def hello():
    a = 5
    b = 0
    i = a/b
    return "Hello World!"

