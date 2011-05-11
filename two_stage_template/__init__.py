import logging

import request_handler
from two_stage_template import monkey_patches

def two_stage_render():
    def decorator(target):
        def wrapper(*args, **kwargs):
            monkey_patches.patch()
            return target(*args, **kwargs)
        return wrapper
    return decorator

class TwoStageTest(request_handler.RequestHandler):

    @two_stage_render()
    def get(self):
        template_values = {
            "sheep": 1,
            "monkey": "ooh ooh aah aah",
        }

        self.render_template("two_stage_template/two_stage_test.html", template_values)


