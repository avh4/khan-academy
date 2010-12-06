import re
import subprocess
import os
import optparse

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

def deploy(version):
    print "Deploying version " + str(version)
    os.system("appcfg.py -V " + str(version) + " update .")

def main():

    parser = optparse.OptionParser()
    parser.add_option('-f', '--force',
        action="store_true", dest="force",
        help="Force deploy even with local changes", default=False)
    options, args = parser.parse_args()

    if not options.force:
        if svn_st():
            print "Local changes found in this directory, canceling deploy."
            return

    version = svn_up()
    if version <= 0:
        print "Could not find version in 'svn up' output."
        return

    deploy(version)

if __name__ == "__main__":
    main()
