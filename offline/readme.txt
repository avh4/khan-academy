This directory is for creating an offline capable version of the Khan Academy.
It only works on windows right now.  Run setup.py to create a zip file of the 
development server for distribution. It will have the filename KhanAcademy-rNNN.zip
where NNN is the latest revision number on http://code.google.com/p/khanacademy/source/list
and can be uploaded to http://code.google.com/p/khanacademy/downloads/list.

To download the videos from archive.org/youtube, run download_ALL.bat in the download_scripts 
directory, or one of the playlist versions.

You can then run setup.py again (or any compression program on the "offline\Khan Academy"
directory) to create a distibution file with videos included. It will contain whatever set 
of lessons you downloaded in the step above to the videos directory.  Be sure to delete any 
7z archives in the download_scripts directory that aren't needed.