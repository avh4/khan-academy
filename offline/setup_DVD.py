import sys, os, traceback, shutil
from os.path import join

from setup import offline_dir, ka_dir, replace_in_file, get_khanacademy_code
sys.path.append("Khan Academy/code/khanacademy-stable")
from topics_list import DVDs_dict


# run setup.py before running this script


readme_text = """
This is version %s of the Khan Academy %s DVD.
The changes since the last version can be seen here:
http://code.google.com/p/khanacademy/source/list

Click on run.bat to start up the server and load the local version of the 
Khan Academy homepage in your browser.   

Let us know how this worked for you at the following address:
khan-academy-comments@googlegroups.com

If there are any bugs in the distribution, you can write a problem report here:
http://code.google.com/p/khanacademy/issues/entry
"""

videos_dir = "C:/Users/Administrator/Desktop/offline/Khan Academy/videos/"
        
        
def get_mangled_playlist_name(playlist_name):
    for char in " :()":
        playlist_name = playlist_name.replace(char, "")
    return playlist_name
    
    
def copy_to_staging(DVD_name, staging_drive):
    revision = get_khanacademy_code()
    staging_dir = staging_drive + "/Khan Academy"
    print "copying", ka_dir, "to", staging_dir
    os.mkdir(staging_dir)
    for root, dirs, files in os.walk(ka_dir):
        for directory in dirs:
            path = staging_drive + root[len(offline_dir)+1:] + "/" + directory
            if not ".svn" in path and not "download_scripts" in path:
                if not os.path.exists(path):
                    os.mkdir(path)            
        for fileName in files:
            path = staging_drive + root[len(offline_dir)+1:]
            if not ".svn" in path and not "download_scripts" in path:
                shutil.copy(join(root,fileName), join(path,fileName))                     

    os.chdir(staging_dir)  
    replace_in_file("run.bat", "rem --use_sqlite giving intermittent errors", '"%~dp0/code/Python25/python.exe" "%~dp0/code/copy_datastore.py"')
    replace_in_file("run.bat",
        '"%~dp0/code/Python25/python.exe" "%~dp0/code/google_appengine/dev_appserver.py" --datastore_path="%~dp0/code/dev_appserver.datastore" "%~dp0/code/khanacademy-stable"',
        '"%~dp0/code/Python25/python.exe" "%~dp0/code/google_appengine/dev_appserver.py" "%~dp0/code/khanacademy-stable"')        
    file = open("readme.txt", "w")
    file.write(readme_text % (revision, DVD_name))
    file.close()
    os.chdir(staging_dir + "/code/khanacademy-stable")
    replace_in_file("topics_list.py", "DVDs_dict.get(None)", "DVDs_dict.get('" + DVD_name + "')")    
        
    os.chdir(staging_dir + "/code")
    for playlist in DVDs_dict[DVD_name]:
        playlist_name = get_mangled_playlist_name(playlist)
        print "copying", videos_dir + playlist_name, "to", staging_dir + '/videos/' + playlist_name
        shutil.copytree(videos_dir + playlist_name, staging_dir + '/videos/' + playlist_name)
                               
    
        
if __name__ == "__main__":
    try:
        DVD_name = sys.argv[1]
        staging_drive = sys.argv[2]
        if DVD_name in DVDs_dict.keys():            
            copy_to_staging(DVD_name, staging_drive)
        else:
            print "first argument should be one of", DVDs_dict.keys()
    except:
        print 'usage: setup_for_DVD.py "DVD name" "staging_drive"'
        traceback.print_exc()
