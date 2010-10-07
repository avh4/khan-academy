rem --use_sqlite is giving "ReferenceProperty failed to be resolved" for library_content
"%~dp0/code/Python25/python.exe" "%~dp0/code/google_appengine/dev_appserver.py" --address=0.0.0.0 --datastore_path="%~dp0/code/dev_appserver.datastore" "%~dp0/code/khanacademy-read-only"
