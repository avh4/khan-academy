import os, zipfile, sys, traceback, shutil, subprocess
from os.path import join
from urllib import urlretrieve
from unzip import unzip
    

offline_dir = os.getcwd()
ka_dir = offline_dir + "/Khan Academy"
code_dir = ka_dir + "/code"
    
    
def replace_in_file(filename, oldstring, newstring):
    try:
        file = open(filename, "r")
        data = file.read()
        file.close()
        file = open(filename, "w")
        data = data.replace(oldstring, newstring)
        file.write(data)
        file.close()
    except:
        traceback.print_exc()
        
        
def download_appengine(appengine_zip): 
    os.chdir(code_dir)
    if not os.path.exists("google_appengine"):
        print "downloading", appengine_zip
        urlretrieve("http://googleappengine.googlecode.com/files/"+appengine_zip, appengine_zip)
        un = unzip()
        un.extract(appengine_zip, ".")    
        os.remove(appengine_zip)    
        replace_in_file("google_appengine/google/appengine/tools/appcfg.py", "if nag.opt_in is None:", "if False:") 
        replace_in_file("google_appengine/google/appengine/tools/dev_appserver.py", 
            "MAX_RUNTIME_RESPONSE_SIZE = 10 << 20", "MAX_RUNTIME_RESPONSE_SIZE = 10 << 22") 
            

def get_khanacademy_code():
    revision = ""  
    os.chdir(code_dir)
    if os.path.exists("khanacademy-read-only"): 
        print "updating code"
        os.chdir(code_dir + "/khanacademy-read-only")
        output = subprocess.Popen(['svn', 'update'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
        revision = ""    
        for line in output.split("\n"):
            if "At revision" in line:
                revision = "r" + line.split()[-1][:-1]    
    else:
        print "checking out khanacademy-read-only"
        output = subprocess.Popen(['svn', 'checkout', 'http://khanacademy.googlecode.com/svn/trunk/', 'khanacademy-read-only'], 
            stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]  
        for line in output.split("\n"):
            if "Checked out revision" in line:
                revision = "r" + line.split()[-1][:-1]
    print "At revision", revision
    return revision
    
    
def copy_python25():
    os.chdir(code_dir)
    if not os.path.exists("Python25"):    
        #urlretrieve("http://www.python.org/ftp/python/2.5/python-2.5.msi", "python-2.5.msi")
        #os.system("python-2.5.msi")
    
        #copy python installation from sys.executable
        #could leave out some stuff to make it smaller
        print "copying python25"        
        items = sys.executable.split("\\")
        python_dir = "\\".join(items[:-1])
        shutil.copytree(python_dir, "Python25")
        

def upload_sample_data(): 
    # clear the datastore
    command = '"%s/Python25/python.exe" "%s/google_appengine/dev_appserver.py" -c "%s/khanacademy-read-only"' % (code_dir, code_dir, code_dir)
    subprocess.Popen(command)
    print "uploading sample data" 
    os.chdir(code_dir + "/khanacademy-read-only/sample_data/")
    os.system("sample_data.py upload --appcfg=../../google_appengine/appcfg.py")


def copy_datastore():
    print "copying datastore" 
    # capture path from dev_appserver.py  (Default c:\users\admini~1\appdata\local\temp\1\dev_appserver.datastore)
    os.chdir(code_dir + "/google_appengine")
    output = subprocess.Popen(['python', 'dev_appserver.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
    for line in output.split("\n"):
        if "dev_appserver.datastore" in line:
            datastore_path = line.split()[-1][:-1]
            shutil.copy(datastore_path, "../")
            break


def generate_library_content():
    print "generating library content"
    os.chdir(code_dir + "/khanacademy-read-only")
    urlretrieve("http://localhost:8080/library_content", "library_content.html")
    
    
def zip_directory(revision):
    print "zipping Khan Academy" 
    os.chdir(offline_dir)
    zip = zipfile.ZipFile("KhanAcademy-" + revision + ".zip", "w")
    for root, dirs, files in os.walk(ka_dir):
         for fileName in files:
             #print join(root,fileName)
             zipDir = root[len(offline_dir)+1:]
             try:
                 zip.write(join(root,fileName), join(zipDir,fileName), zipfile.ZIP_DEFLATED)
             except:
                 traceback.print_exc()

            
if __name__ == "__main__":                     

    download_appengine("google_appengine_1.3.7.zip")
    revision = get_khanacademy_code()
    copy_python25()
    upload_sample_data()
    copy_datastore()
    generate_library_content()
    zip_directory(revision)
    sys.exit()
    #TODO: upload it somewhere                                       
                                       
