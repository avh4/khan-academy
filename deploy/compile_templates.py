# -*- coding: utf-8 -*-
import logging
import os
import shutil
import sys

sys.path.append(os.path.abspath("."))

import jinja2

# Modified from tipfy's template compilation steps

def compile_templates():

    src_path = os.path.join(os.path.dirname(__file__), "..", "templates")
    dest_path = os.path.join(os.path.dirname(__file__), "..", "compiled_templates")

    config = {
        "autoescape": False, 
        "extensions": [],
        "loader": jinja2.FileSystemLoader(src_path)
    }

    env = jinja2.Environment(**config)
    env.filters.update({
        "escapejs": lambda: "",
        "urlencode": lambda: "",
        "static_url": lambda: "",
        "slugify": lambda: "",
        "find_column_index": lambda: "",
        "in_list": lambda: "",
        "column_height": lambda: "",
        "thousands_separated": lambda: "",
    })

    env.globals.update({
        "css_package": "",
        "js_package": "",
        "render_xsrf_js": "",
        "login_notifications": "",
        "badge_notifications": "",
        "badge_counts": "",
        "profiler_includes": "",
        "mailing_list_signup_form": "",
        "playlist_browser": "",
        "column_major_sorted_videos": "",
        "UserData": "",
        "hash": "",
        "App": "",
    })

    try:
        shutil.rmtree(dest_path)
    except:
        pass

    env.compile_templates(dest_path, extensions=None, 
            ignore_errors=False, py_compile=False, zip=None,
            filter_func=filter_templates)

def filter_templates(src):
    return os.path.basename(src).endswith(".html")

if __name__ == "__main__":
    compile_templates()
