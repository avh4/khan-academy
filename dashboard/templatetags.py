import os
import logging

import template_cached
register = template_cached.create_template_register()

@register.inclusion_tag("dashboard/daily_graph.html")
def dashboard_daily_graph(name, title, y_axis, counts):
    return { "name": name, "title": title, "y_axis": y_axis, "counts": counts }

