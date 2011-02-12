import os, zipfile, sys, traceback, shutil, subprocess, time
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
        replace_in_file("google_appengine/google/appengine/tools/dev_appserver_main.py", 
            "http_server.serve_forever()", "import webbrowser; webbrowser.open('http://localhost:8080'); http_server.serve_forever()")             
        replace_in_file("google_appengine/google/appengine/tools/bulkloader.py", "self.num_threads = arg_dict['num_threads']", "self.num_threads = 5")             
            


def get_khanacademy_code():
    revision = ""  
    os.chdir(code_dir)
    output = ""
    if os.path.exists("khanacademy-read-only"): 
        print "updating code"
        os.chdir(code_dir + "/khanacademy-read-only")
        output = subprocess.Popen(['svn', 'update'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
        revision = ""    
        for line in output.split("\n"):
            if "At revision" in line or "Updated to revision" in line:
                revision = "r" + line.split()[-1][:-1]
    else:
        print "checking out khanacademy-read-only"
        output = subprocess.Popen(['svn', 'checkout', 'http://khanacademy.googlecode.com/svn/trunk/', 'khanacademy-read-only'], 
            stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]  
        for line in output.split("\n"):
            if "Checked out revision" in line:
                revision = "r" + line.split()[-1][:-1]
    if revision:
        print "At revision", revision
    else:
        print "output:\n" + output
    os.chdir(code_dir + "/khanacademy-read-only")
    replace_in_file("app.py", "offline_mode = False", "offline_mode = True")
    replace_in_file("app.yaml", "static_dir: offline/Khan Academy/videos", "static_dir: ../../videos")             
    return revision


def insert_revision_in_readme(revision):    
    os.chdir(ka_dir)
    replace_in_file("readme.txt", "{{version_number}}", revision)    
    
    
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
        

def download_7zip():
    os.chdir(code_dir)
    if not os.path.exists("7za.exe"):
        print "downloading 7zip"   
        urlretrieve("http://downloads.sourceforge.net/project/sevenzip/7-Zip/4.65/7za465.zip", "7za465.zip")
        un = unzip()
        un.extract("7za465.zip", ".")    
        os.remove("7za465.zip")     


def download_highcharts():
    os.chdir(code_dir)
    if not os.path.exists("khanacademy-read-only/javascript/highcharts.js"):
        print "downloading highcharts"   
        urlretrieve("http://highcharts.com/downloads/zips/Highcharts-2.1.1.zip", "Highcharts-2.1.1.zip")
        zf = zipfile.ZipFile("Highcharts-2.1.1.zip")
        file = open(code_dir+"/khanacademy-read-only/javascript/highcharts.js", 'wb')
        file.write(zf.read("js/highcharts.js"))
        file.close()   
        zf.close()
        os.remove("Highcharts-2.1.1.zip") 
             
             
def download_vlc():
    os.chdir(ka_dir)
    if not os.path.exists("vlc-1.1.5-win32.exe"):
        print "downloading vlc"   
        urlretrieve("http://downloads.sourceforge.net/project/vlc/1.1.5/win32/vlc-1.1.5-win32.exe?r=&ts=1292520846&use_mirror=ignum2", 
            "vlc-1.1.5-win32.exe")
        
        
def upload_sample_data(): 
    # --use_sqlite giving intermittent errors
    command = '"%s/Python25/python.exe" "%s/google_appengine/dev_appserver.py" --clear_datastore "%s/khanacademy-read-only"' % (code_dir, code_dir, code_dir)
    subprocess.Popen(command)
    print "giving time for server to start" 
    time.sleep(20)
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
    

def generate_video_mapping():
    print "generating video_mapping.py"
    os.chdir(code_dir)
    urlretrieve("http://localhost:8080/video_mapping", "video_mapping.py")
    

def remove_bulkloader_logs():
    sd_dir = code_dir + "/khanacademy-read-only/sample_data"
    for filename in os.listdir(sd_dir):
        if filename.startswith("bulkloader"):
            os.remove(sd_dir + "/" + filename)
    

def create_download_scripts():
    sys.path.append(code_dir)
    from video_mapping import video_mapping  

    playlists = video_mapping.keys()
    playlists.sort()

    for playlist in playlists:
        file = open(ka_dir + "/download_scripts/download_" + playlist + ".bat", "w")
        file.write('"%~dp0/../code/Python25/python.exe" "%~dp0/../code/download.py" ' + playlist)    
        file.close()

    file = open(ka_dir + "/download_scripts/download_ALL.bat", "w")
    for playlist in playlists:
        file.write('call "download_' + playlist + '.bat"\n')
    file.close()


def zip_directory(revision):
    print "zipping Khan Academy" 
    os.chdir(offline_dir)
    zip = zipfile.ZipFile("KhanAcademy-" + revision + ".zip", "w")
    for root, dirs, files in os.walk(ka_dir):
         for fileName in files:
             if not ".svn" in join(root,fileName):
                 #print join(root,fileName)
                 zipDir = root[len(offline_dir)+1:]
                 try:
                     zip.write(join(root,fileName), join(zipDir,fileName), zipfile.ZIP_DEFLATED)
                 except:
                     traceback.print_exc()
                     
def revert_readme(revision):
    os.chdir(ka_dir)    
    replace_in_file("readme.txt", revision, "{{version_number}}")        
   

def setup():
    download_appengine("google_appengine_1.4.2.zip")
    revision = get_khanacademy_code()
    insert_revision_in_readme(revision)
    copy_python25()
    download_7zip()
    download_highcharts()
    download_vlc()
    upload_sample_data()
    copy_datastore()
    generate_video_mapping()
    remove_bulkloader_logs()
    create_download_scripts()
    zip_directory(revision)
    revert_readme(revision)
    sys.exit()
    #TODO: upload it http://code.google.com/p/khanacademy/downloads/list ?                                     

                                       
if __name__ == "__main__":  
    setup()
    
    