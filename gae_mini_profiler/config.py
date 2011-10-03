from google.appengine.api import users

# If using the default should_profile implementation, the profiler
# will only be enabled for requests made by the following GAE users.
enabled_profiler_emails = [
    "kamens@gmail.com",
    "jasonrosoff@gmail.com",
    "joelburget@gmail.com",
    "dmnd@desmondbrand.com",
    "marcia.lee@gmail.com",
    "spicyjalapeno@gmail.com",
    "ParkerKuivila@gmail.com",
    "jace.kohlmeier@gmail.com",
    "davidhu91@gmail.com",
    "marcos@khanacademy.org",
    "tallnerd@gmail.com",
]

# Customize should_profile to return true whenever a request should be profiled.
# This function will be run once per request, so make sure its contents are fast.
class ProfilerConfigProduction:
    @staticmethod
    def should_profile(environ):
        user = users.get_current_user()
        return user and user.email() in enabled_profiler_emails

class ProfilerConfigDevelopment:
    @staticmethod
    def should_profile(environ):
        return users.is_current_user_admin()
