from __future__ import with_statement
import re
import subprocess
import os
import optparse
import StringIO
import base64

import compress

def popen_results(args):
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    return proc.communicate()[0]

def hg_st():

    output = popen_results(['hg', 'st', '-mard'])
    return len(output) > 0

def hg_pull_up():

    version = -1
    pattern = re.compile("^changeset:\\s+\\d+:(.+)$")

    # Pull latest
    popen_results(['hg', 'pull'])

    # Hg up and make sure we didn't hit a merge
    output = popen_results(['hg', 'up'])
    lines = output.split("\n")
    if len(lines) != 2 or lines[0].find("files updated") < 0:
        # Ran into merge or other problem
        return version

    # Grab the tip changeset hash
    output = popen_results(['hg', 'tip'])
    lines = output.split("\n")
    for line in lines:
        match = pattern.match(line)
        if match:
            version = match.groups()[0]

    return version

# def replace_data_uri():
#     print "Replacing images with data-uris"
#     path = os.path.join(os.path.dirname(__file__), "..")
#     replace_data_uri_in_path(path)
# 
# def compile_file(filename):
#     filename = os.path.join('..', filename)
#     print "filename: %s" % filename
#     if os.path.isfile(filename):
#         with open(filename) as img:
#             f = StringIO.StringIO()
#             f.write(img.read())
#             return 'data:image/png;base64,'+base64.b64encode(f.getvalue())
# 
#     return filename
# 
# def replace_data_uri_in_path(path):
#     # only go through css, html, and js. We're assuming we don't need to
#     # replace any filenames in python.
#     if not os.path.exists(path):
#         raise Exception("Path does not exist: %s" % path)
# 
#     # Essentially grep for 'data-uri' in each file in the
#     # directory (and its children), taken from a stack overflow answer:
#     # http://stackoverflow.com/questions/1863236/grep-r-in-python/1863274#1863274
#     r = re.compile('data-uri\(/images/(\S+)\.(png|gif|GIF|jpg)\)')
#         
#     for parent, dnames, fnames in os.walk(dir):
#         for fname in fnames:
#             filename = os.path.join(parent, fname)
#             extension = os.path.splitext(filename)[1]
#             if os.path.isfile(filename) and extension in ['css']: #'html'
#                 with open(filename) as f:
#                     for line in f:
#                         if r.search(line):
#                             for i in r.finditer(line):
#                                 #r = re.compile('/images/(\S+)\.(png|gif|GIF|jpg)')
#                                 #r.sub(replace, line)
#                                 filename = '/images/'+i.group(1)+'.'+i.group(2)
#                                 print "filename: %s" % filename
#                                 # re.sub(filename, compile_file, line)
#                                 print compile_file(filename)

def compress_js():
    print "Compressing javascript"
    path = os.path.join(os.path.dirname(__file__), "..", "javascript")
    compress.compress_all_javascript(path)

def compress_css():
    print "Compressing stylesheets"
    path = os.path.join(os.path.dirname(__file__), "..", "stylesheets")
    compress.compress_all_stylesheets(path)

def deploy(version):
    print "Deploying version " + str(version)
    os.system("appcfg.py -V " + str(version) + " update .")

def main():

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

    parser.add_option('-d', '--dryrun',
        action="store_true", dest="dryrun",
        help="Dry run without the final deploy-to-App-Engine step", default=False)

    options, args = parser.parse_args()

    if not options.force:
        if hg_st():
            print "Local changes found in this directory, canceling deploy."
            return

    version = -1

    if not options.noup or len(options.version) == 0:
        version = hg_pull_up()
        if version <= 0:
            print "Could not find version after 'hg pull', 'hg up', 'hg tip'."
            return

    if len(options.version) > 0:
        version = options.version

    print "Deploying version " + str(version)
    compress.revert_js_css_hashes()
    #replace_data_uri()
    compress_js()
    compress_css()

    if not options.dryrun:
        deploy(version)
        compress.revert_js_css_hashes()

if __name__ == "__main__":
    main()
