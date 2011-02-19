import re
import subprocess
import os
import optparse

import compress

def popen_results(args):
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    return proc.communicate()[0]

def svn_st():

    output = popen_results(['svn', 'st', '-q', '--ignore-externals'])
    return len(output) > 0

def svn_up():

    version = -1
    pattern = re.compile("^(At|Updated to) revision (\\d+)\.$")

    output = popen_results(['svn', 'up'])
    lines = output.split("\n")
    for line in lines:
        match = pattern.match(line)
        if match:
            version = int(match.groups()[1])

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
        action="store", dest="noup",
        help="Don't svn up before deploy", default="")

    parser.add_option('-d', '--dryrun',
        action="store_true", dest="dryrun",
        help="Dry run without the final deploy-to-App-Engine step", default=False)

    options, args = parser.parse_args()

    if not options.force:
        if svn_st():
            print "Local changes found in this directory, canceling deploy."
            return

    if not options.noup or len(options.version) == 0:
        version = svn_up()
        if version <= 0:
            print "Could not find version in 'svn up' output."
            return

    if len(options.version) > 0:
        version = options.version

    compress_js()
    compress_css()

    if not options.dryrun:
        deploy(version)

if __name__ == "__main__":
    main()
