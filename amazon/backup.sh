#!/bin/sh

# Remove old bulkloader log files
rm bulkloader-*

# Gzip results
gzip *.dat
gzip *.log

# Backup entire datastore
google_appengine/appcfg.py download_data --application=khanexercises --url=http://khanexercises.appspot.com/remote_api --filename=`date +%F.dat` --email=kamens@gmail.com --passin < private_pw > `date +%F.log`

