This directory is for creating an offline capable version of the Khan Academy.
It's only works on windows right now.  Run setup.py to create a zip file of the 
development server for distribution. It will have the filename KhanAcademy-rNNN.zip
where NNN is the revision number on http://code.google.com/p/khanacademy/source/list
and can be uploaded to http://code.google.com/p/khanacademy/downloads/list.

To download the videos from youtube, run download_ALL.bat in the download_scripts
directory, or one of the playlist versions.

Once you have downloaded a playlist, you can upload it to archive.org using the script
upload_zipped_playlists.py.  You can upload individual videos to archive.org using
upload_individual_videos.py.