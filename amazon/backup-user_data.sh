#!/bin/sh

cd /home/ec2-user

# Backup UserData entities w/ most important data (points, proficiencies, badges)
google_appengine/appcfg.py download_data --application=khanexercises --kind=UserData --url=http://khanexercises.appspot.com/remote_api --filename=`date +%F.user_data.dat` --email=kamens@gmail.com --passin < private_pw > `date +%F.user_data.log`

gzip -f *.user_data.dat
gzip -f *.user_data.log

google_appengine/appcfg.py download_data --application=khanexercises --kind=UserExercise --url=http://khanexercises.appspot.com/remote_api --filename=`date +%F.user_exercises.dat` --email=kamens@gmail.com --passin < private_pw > `date +%F.user_exercises.log`

gzip -f *.user_exercises.dat
gzip -f *.user_exercises.log

for f in *.user_*.*.gz
do
  echo "Moving $f to s3 bucket"
  s3cmd-1.0.0/s3cmd put $f s3://KA-user_data-backups/$f
done

# Delete files older than 1 week
find *.gz -mtime +7 -exec rm {} \;
find *.log -mtime +7 -exec rm {} \;
find *.dat -mtime +7 -exec rm {} \;
find *.sql3 -mtime +7 -exec rm {} \;

