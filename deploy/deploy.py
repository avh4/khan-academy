import sys
import re
import subprocess
import os
import optparse
import datetime
import urllib2
import webbrowser
import re
import getpass

sys.path.append(os.path.abspath("."))
import compress
import glob
import tempfile

try:
    import secrets
    hipchat_deploy_token = secrets.hipchat_deploy_token
except Exception, e:
    print "Exception raised while trying to import secrets. Attempting to continue..."
    print repr(e)
    hipchat_deploy_token = None

try:
    from secrets import app_engine_username, app_engine_password
except Exception, e:
    (app_engine_username, app_engine_password) = (None, None)

if hipchat_deploy_token:
    import hipchat.room
    import hipchat.config
    hipchat.config.manual_init(hipchat_deploy_token)

def popen_results(args):
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    return proc.communicate()[0]

def popen_return_code(args, input=None):
    proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    proc.communicate(input)
    return proc.returncode

def get_app_engine_credentials():
    if app_engine_username and app_engine_password:
        print "Using password for %s from secrets.py" % app_engine_username
        return (app_engine_username, app_engine_password)
    else:
        email = raw_input("App Engine Email: ")
        password = getpass.getpass("Password for %s: " % email)
        return (email, password)

def send_hipchat_deploy_message(version, includes_local_changes, email):
    if hipchat_deploy_token is None:
        return

    app_id = get_app_id()
    if app_id != "khan-academy":
        # Don't notify hipchat about deployments to test apps
        print 'Skipping hipchat notification as %s looks like a test app' % app_id
        return

    url = "http://%s.%s.appspot.com" % (version, app_id)

    hg_id = hg_version()
    hg_msg = hg_changeset_msg(hg_id)
    kiln_url = "https://khanacademy.kilnhg.com/Search?search=%s" % hg_id

    git_id = git_version()
    git_msg = git_revision_msg(git_id)
    github_url = "https://github.com/Khan/khan-exercises/commit/%s" % git_id

    local_changes_warning = " (including uncommitted local changes)" if includes_local_changes else ""
    message_tmpl = """
            %(hg_id)s%(local_changes_warning)s to <a href='%(url)s'>a non-default url</a>. Includes
            website changeset "<a href='%(kiln_url)s'>%(hg_msg)s</a>" and khan-exercises
            revision "<a href='%(github_url)s'>%(git_msg)s</a>."
            """ % {
                "url": url,
                "hg_id": hg_id,
                "kiln_url": kiln_url,
                "hg_msg": hg_msg,
                "github_url": github_url,
                "git_msg": git_msg,
                "local_changes_warning": local_changes_warning,
            }
    public_message = "Just deployed %s" % message_tmpl
    private_message = "%s just deployed %s" % (email, message_tmpl)
    
    hipchat_message(public_message, ["Exercises"])
    hipchat_message(private_message, ["1s and 0s"])

def hipchat_message(msg, rooms):
    if hipchat_deploy_token is None:
        return

    for room in hipchat.room.Room.list():

        if room.name in rooms:

            result = ""
            msg_dict = {"room_id": room.room_id, "from": "Mr Monkey", "message": msg, "color": "purple"}

            try:
                result = str(hipchat.room.Room.message(**msg_dict))
            except:
                pass

            if "sent" in result:
                print "Notified Hipchat room %s" % room.name
            else:
                print "Failed to send message to Hipchat: %s" % msg

def get_app_id():
    f = open("app.yaml", "r")
    contents = f.read()
    f.close()

    app_re = re.compile("^application:\s+(.+)$", re.MULTILINE)
    match = app_re.search(contents)

    return match.groups()[0]

def hg_st():
    output = popen_results(['hg', 'st', '-mard', '-S'])
    return len(output) > 0

def hg_pull_up():
    # Pull latest
    popen_results(['hg', 'pull'])

    # Hg up and make sure we didn't hit a merge
    output = popen_results(['hg', 'up'])
    lines = output.split("\n")
    if len(lines) != 2 or lines[0].find("files updated") < 0:
        # Ran into merge or other problem
        return -1

    return hg_version()

def hg_version():
    # grab the tip changeset hash
    current_version = popen_results(['hg', 'identify','-i']).strip()
    return current_version or -1

def hg_changeset_msg(changeset_id):
    # grab the summary and date
    output = popen_results(['hg', 'log', '--template','{desc}', '-r', changeset_id])
    return output

def git_version():
    # grab the tip changeset hash
    return popen_results(['git', '--work-tree=khan-exercises/', '--git-dir=khan-exercises/.git', 'rev-parse', 'HEAD']).strip()

def git_revision_msg(revision_id):
    return popen_results(['git', '--work-tree=khan-exercises/', '--git-dir=khan-exercises/.git', 'show', '-s', '--pretty=format:%s', revision_id]).strip()

def check_secrets():
    content = ""

    try:
        f = open("secrets.py", "r")
        content = f.read()
        f.close()
    except:
        return False

    # Try to find the beginning of our production facebook app secret
    # to verify deploy is being sent from correct directory.
    regex = re.compile("^facebook_app_secret = '050c.+'$", re.MULTILINE)
    return regex.search(content)

def tidy_up():
    """moves all pycs and compressed js/css to a rubbish folder alongside the project"""
    trashdir = tempfile.mkdtemp(dir="../", prefix="rubbish-")
    
    print "Moving old files to %s." % trashdir
    
    junkfiles = open(".hgignore","r")
    please_tidy = [filename.strip() for filename in junkfiles 
                      if not filename.strip().startswith("#")]
    but_ignore = ["secrets.py", "", "syntax: glob"]
    [please_tidy.remove(path) for path in but_ignore]
    
    for root, dirs, files in os.walk("."):
        if ".git" in dirs:
            dirs.remove(".git")
        if ".hg" in dirs:
            dirs.remove(".hg")
        
        for dirname in dirs:
            removables = [glob.glob( os.path.join(root, dirname, rubbish) ) for rubbish in please_tidy
                          if len( glob.glob( os.path.join(root, dirname, rubbish) ) ) > 0]
            # flatten sublists of removable filse
            please_remove = [filename for sublist in removables for filename in sublist]
            if please_remove:
                [ os.renames(stuff, os.path.join(trashdir,stuff)) for stuff in please_remove ]
    

def compress_js():
    print "Compressing javascript"
    compress.compress_all_javascript()

def compress_css():
    print "Compressing stylesheets"
    compress.compress_all_stylesheets()

def compile_templates():
    print "Compiling all templates"
    return 0 == popen_return_code(['python', 'deploy/compile_templates.py'])

def prime_autocomplete_cache(version):
    try:
        resp = urllib2.urlopen("http://%s.%s.appspot.com/api/v1/autocomplete?q=calc" % (version, get_app_id()))
        resp.read()
        print "Primed autocomplete cache"
    except:
        print "Error when priming autocomplete cache"

def open_browser_to_ka_version(version):
    webbrowser.open("http://%s.%s.appspot.com" % (version, get_app_id()))

def deploy(version, email, password):
    print "Deploying version " + str(version)
    return 0 == popen_return_code(['appcfg.py', '-V', str(version), "-e", email, "--passin", "update", "."], "%s\n" % password)

def main():

    start = datetime.datetime.now()

    parser = optparse.OptionParser()

    parser.add_option('-f', '--force',
        action="store_true", dest="force",
        help="Force deploy even with local changes", default=False)

    parser.add_option('-v', '--version',
        action="store", dest="version",
        help="Override the deployed version identifier", default="")

    parser.add_option('-x', '--no-up',
        action="store_true", dest="noup",
        help="Don't hg pull/up before deploy", default="")

    parser.add_option('-s', '--no-secrets',
        action="store_true", dest="nosecrets",
        help="Don't check for production secrets.py file before deploying", default="")

    parser.add_option('-d', '--dryrun',
        action="store_true", dest="dryrun",
        help="Dry run without the final deploy-to-App-Engine step", default=False)

    parser.add_option('-c', '--clean',
        action="store_true", dest="clean",
        help="Clean the old packages and generate them again. If used with -d,the app is not compiled at all and is only cleaned.", default=False)

    options, args = parser.parse_args()

    if(options.clean):
        print "Cleaning previously generated files"
        tidy_up()
        if options.dryrun:
            return
        
    includes_local_changes = hg_st()
    if not options.force and includes_local_changes:
        print "Local changes found in this directory, canceling deploy."
        return

    version = -1

    if not options.noup or len(options.version) == 0:
        version = hg_pull_up()
        if version <= 0:
            print "Could not find version after 'hg pull', 'hg up', 'hg tip'."
            return

    if not options.nosecrets:
        if not check_secrets():
            print "Stopping deploy. It doesn't look like you're deploying from a directory with the appropriate secrets.py."
            return

    if len(options.version) > 0:
        version = options.version

    if options.clean:
        compress.hashes = {}

    print "Deploying version " + str(version)
    compress.revert_js_css_hashes()

    if not compile_templates():
        print "Failed to compile templates, bailing."
        return

    compress_js()
    compress_css()

    if not options.dryrun:
        (email, password) = get_app_engine_credentials()
        success = deploy(version, email, password)
        compress.revert_js_css_hashes()
        if success:
            send_hipchat_deploy_message(version, includes_local_changes, email)
            open_browser_to_ka_version(version)
            prime_autocomplete_cache(version)

    end = datetime.datetime.now()
    print "Done. Duration: %s" % (end - start)

if __name__ == "__main__":
    main()
