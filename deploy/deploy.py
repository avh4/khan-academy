import re
import subprocess
import os
import optparse

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

def compress_js():
    print "Compressing javascript"
    path = os.path.join(os.path.dirname(__file__), "..", "javascript")
    compress.compress_all_packages(path, ".js")

def compress_css():
    print "Compressing stylesheets"
    path = os.path.join(os.path.dirname(__file__), "..", "stylesheets")
    compress.compress_all_packages(path, ".css")

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
    compress_js()
    compress_css()

    if not options.dryrun:
        deploy(version)

if __name__ == "__main__":
    main()
