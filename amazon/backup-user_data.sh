#!/bin/sh

cd /home/ec2-user

# Backup UserData entities w/ most important data (points, proficiencies, badges)
google_appengine/appcfg.py download_data --application=khanexercises --kind=UserData --url=http://khanexercises.appspot.com/remote_api --filename=`date +%F.user_data.dat` --email=kamens@gmail.com --passin < private_pw > `date +%F.user_data.log`

# Gzip results
gzip -f *.user_data.dat
gzip -f *.user_data.log

for f in *.user_data.*.gz
do
  echo "Moving $f to s3 bucket"
  s3cmd-1.0.0/s3cmd put $f s3://KA-user_data-backups/$f
done

# Delete files older than 2 weeks
find *.gz -mtime +14 -exec rm {} \;


