from request_handler import RequestHandler
import os

class RobotsTxt(RequestHandler):
    """Dynamic robots.txt that hides staging apps from search engines"""
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'

        if os.environ['SERVER_NAME'] == 'www.khanacademy.org':
            self.response.write("User-agent: *\n")
            self.response.write("Disallow:")
        else:
            self.response.write("User-agent: *\n")
            self.response.write("Disallow: *")
