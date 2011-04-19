rem --use_sqlite giving intermittent errors
rem --address=0.0.0.0 gives problems with some computers
"%~dp0/code/Python25/python.exe" "%~dp0/code/google_appengine/dev_appserver.py" --datastore_path="%~dp0/code/dev_appserver.datastore" "%~dp0/code/khanacademy-stable"
