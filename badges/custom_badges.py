import logging

from google.appengine.api import users

import request_handler
from badges import Badge, BadgeContextType, BadgeCategory
from models_badges import CustomBadgeType
from models import UserData

class CustomBadge(Badge):

    @staticmethod
    def all():
        custom_badges = []
        custom_badge_types = CustomBadgeType.all().fetch(1000)
        for custom_badge_type in custom_badge_types:
            custom_badges.append(CustomBadge(custom_badge_type))
        return custom_badges

    def __init__(self, custom_badge_type):
        Badge.__init__(self)
        self.is_hidden_if_unknown = True

        self.name = custom_badge_type.key().name()
        self.description = custom_badge_type.description
        self.full_description = custom_badge_type.full_description
        self.points = custom_badge_type.points
        self.badge_category = custom_badge_type.category

    def is_satisfied_by(self, *args, **kwargs):
        return False # Custom badges are only handed out manually

    def extended_description(self):
        return self.full_description

class CreateCustomBadge(request_handler.RequestHandler):
    def get(self):
        if not users.is_current_user_admin():
            return
        
        template_values = {
                "badge_categories": BadgeCategory.empty_count_dict().keys(),
                "failed": self.request_bool("failed", default=False),
                }

        self.render_template("badges/create_custom_badge.html", template_values)

    def post(self):
        if not users.is_current_user_admin():
            return

        name = self.request_string("name")
        description = self.request_string("description")
        full_description = self.request_string("full_description")
        points = self.request_int("points", default = -1)
        badge_category = self.request_int("badge_category", default = -1)

        # Create custom badge
        if CustomBadgeType.insert(name, description, full_description, points, badge_category):
            self.redirect("/badges/custom/award")
            return

        self.redirect("/badges/custom/create?failed=1")

class AwardCustomBadge(request_handler.RequestHandler):
    def get(self):
        if not users.is_current_user_admin():
            return

        template_values = {
                "custom_badges": CustomBadge.all(),
                }

        self.render_template("badges/award_custom_badge.html", template_values)

    def post(self):
        if not users.is_current_user_admin():
            return

        custom_badge_name = self.request_string("name", default="")
        custom_badges = CustomBadge.all()
        custom_badge_awarded = None
        emails_awarded = []
        
        for custom_badge in custom_badges:
            if custom_badge.name == custom_badge_name:
                custom_badge_awarded = custom_badge

        if custom_badge_awarded:
            # Award badges and show successful email addresses
            emails_newlines = self.request_string("emails", default="")
            emails = emails_newlines.split()
            emails = map(lambda email: email.strip(), emails)

            for email in emails:
                user = users.User(email)
                user_data = UserData.get_for(user)
                if user_data:
                    if not custom_badge_awarded.is_already_owned_by(user_data):
                        custom_badge_awarded.award_to(user, user_data)
                        user_data.put()
                        emails_awarded.append(email)
        
        template_values = {
                "custom_badges": CustomBadge.all(),
                "custom_badge_awarded": custom_badge_awarded, 
                "emails_awarded": emails_awarded
                }

        self.render_template("badges/award_custom_badge.html", template_values)

