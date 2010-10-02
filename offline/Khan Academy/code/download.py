import sys, os
from video_mapping import video_mapping

os.chdir("../code")
folder = "../videos/" + sys.argv[1]

if not os.path.exists(folder):
    os.mkdir(folder)
for title, youtube_id, readable_id in video_mapping[sys.argv[1]]:
    if os.path.exists(folder + '/' + readable_id + ".flv"):
        print "already downloaded", readable_id
    else:
        os.system('youtube-dl.py -f 34 -icw -o "' + folder + '/' + readable_id + '.flv" http://www.youtube.com/watch?v=' + youtube_id)

