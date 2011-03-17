import request_handler
import consts
import util
from app import App

class AboutRequestHandler(request_handler.RequestHandler):
    def render_template(self, template_name, template_values):
        template_values["selected_nav_link"] = "about"
        request_handler.RequestHandler.render_template(self, template_name, template_values)

class ViewAbout(AboutRequestHandler):
    def get(self):
        self.render_template('about/about-the-site.html', {"selected_id": "the-site", "approx_vid_count": consts.APPROX_VID_COUNT})

class ViewAboutTheTeam(AboutRequestHandler):
    def get(self):
        self.render_template('about/about-the-team.html', {"selected_id": "the-team"})
        
class ViewGettingStarted(AboutRequestHandler):
    def get(self):
        self.render_template('about/getting-started.html', {"selected_id": "getting-started", "approx_vid_count": consts.APPROX_VID_COUNT, "App": App })

class ViewFAQ(AboutRequestHandler):
    def get(self):
        self.render_template('about/faq.html', {"selected_id": "faq", "approx_vid_count": consts.APPROX_VID_COUNT })

class ViewDownloads(AboutRequestHandler):
    def get(self):
        self.render_template('about/downloads.html', {})

