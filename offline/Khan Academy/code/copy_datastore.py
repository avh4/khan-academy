import os, subprocess, shutil

# capture path from dev_appserver.py  (Default c:\users\admini~1\appdata\local\temp\1\dev_appserver.datastore)
cwd = os.getcwd()
os.chdir("code/google_appengine")
output = subprocess.Popen(['python', 'dev_appserver.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
for line in output.split("\n"):
    if "dev_appserver.datastore" in line:
        datastore_path = line.split()[-1][:-1]
        if not os.path.exists(datastore_path):
            shutil.copy(cwd+"/code/dev_appserver.datastore", datastore_path)
        break