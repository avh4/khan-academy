import request_handler
from two_stage_template import monkey_patches

class TwoStageTest(request_handler.RequestHandler):

    #@two_stage_test
    def get(self):

        monkey_patches.patch()

        template_values = {
            "sheep": 1,
            "monkey": "ooh ooh aah aah",
        }

        self.render_template("two_stage_template/two_stage_test.html", template_values)


