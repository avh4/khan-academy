#!/bin/sh

# Remove old bulkloader log files
rm bulkloader-*

# Gzip results
gzip *.dat
gzip *.log

# Backup entire datastore
google_appengine/appcfg.py download_data --application=khanexercises --url=http://khanexercises.appspot.com/remote_api --filename=`date +%F.dat` --email=kamens@gmail.com --passin < private_pw > `date +%F.log`

# Gzip results
gzip *.dat
gzip *.log

for f in *.gz
do
  echo "Moving $f to s3 bucket"
  s3cmd-1.0.0/s3cmd put $f s3://KA-datastore/$f
done

# Delete files older than 2 weeks
find *.gz -mtime +14 -exec rm {} \;

