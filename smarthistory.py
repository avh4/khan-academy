#for blobstore of images
from __future__ import with_statement
from google.appengine.api import files
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.blobstore import BlobInfo

import logging
import layer_cache
import urllib
import urllib2

from models import Setting

import request_handler
from request_handler import RequestHandler

from custom_exceptions import SmartHistoryLoadException 

from datetime import datetime


SMARTHISTORY_CACHE_EXPIRATION_TIME=86400
SMARTHISTORY_IMAGE_CACHE_EXPIRATION=2419200 #28 days
SMARTHISTORY_URL = "http://khan.smarthistory.org"
IGNORE_FIRST_PATH_COMPONENT = 0

def deleteOldBlobs():
    blobs=BlobInfo.all().fetch(500)
    for blob in blobs:
        if blob.filename.find(SMARTHISTORY_URL)!=-1:
            age=datetime.now()-blob.creation
            if age.days*86400+age.seconds>=SMARTHISTORY_IMAGE_CACHE_EXPIRATION:
                blob.delete()

class SmartHistoryProxy(RequestHandler, blobstore_handlers.BlobstoreDownloadHandler):
    def __init__(self):
        self.attempt_counter=0	
	
    def get(self):
        if self.request.get("clearcache"):
            self.clearCache()
        
        data, response_headers, blob_key=self.load_resource()
        
        #might need to convert all dictionary keys to lower case
        #check to see if we need to return 304 - might need to add handling of If-Modified-Since, in case If-None-Match is not sent 
        if self.request.headers.has_key("If-None-Match") and response_headers.has_key("etag") and self.request.headers["If-None-Match"]==response_headers["etag"]:
            logging.info("sending 304 from within the application");
            self.response.headers["Cache-Control"]="public, max-age="+str(SMARTHISTORY_IMAGE_CACHE_EXPIRATION)+";"
            self.response.set_status(304)
            return

        for h in response_headers:
            self.response.headers[h]=response_headers[h]

        if(blob_key):
            logging.info("resending blob with key="+str(blob_key))
            self.send_blob(blob_key)
            return
 
        self.response.out.write(data)
        return 
  		
    def post(self):
        arguments=self.request.arguments()
        post_data={}
        for a in arguments:
            post_data[a]=self.request.get(a)

        path=self.request.path
        if IGNORE_FIRST_PATH_COMPONENT:
            pos= path.find("/",1)
            if pos!=-1:
                path= path[pos:]
   
        try:
            request = urllib2.Request(SMARTHISTORY_URL+path)
            response = urllib2.urlopen(request, urllib.urlencode(post_data))
            data=response.read()     
        # TODO: write better exception handler
        except Exception, e:
            # self.response.out.write("error="+e)
            raise e
            return      

        self.response.out.write(data)   

    def clearCache(self):
        Setting.smarthistory_version(int(Setting.smarthistory_version())+1)  

    #load the resource from smart history's server and then cache it in the data store
    #if it is an image then cache it in the blob store and store the blobkey in the data store 
    @layer_cache.cache_with_key_fxn(lambda self: "smart_history_v%s_%s" % (Setting.smarthistory_version(),self.request.path), expiration=SMARTHISTORY_CACHE_EXPIRATION_TIME, layer=layer_cache.Layers.Datastore, persist_across_app_versions=True)
    def load_resource(self):
        path=self.request.path
        headers=self.request.headers
        logging.info("getting resource "+str(path)+" from "+SMARTHISTORY_URL);
        if IGNORE_FIRST_PATH_COMPONENT:
            pos= path.find("/",1)
            if pos!=-1:
                path= path[pos:]
       
        request = urllib2.Request(SMARTHISTORY_URL+path)
        for h in headers:
            #img is in users browser cache - we don't want to cache a Not-Modified response otherwise people who don't have image in browser cache won't get it
            if not h in ["If-Modified-Since", "If-None-Match", "Content-Length","Host"]:
                request.headers[h]= headers[h]
        
        try:
            response = urllib2.urlopen(request)
            data=response.read()     
        # TODO: write better exception handler
        except Exception, e:
            self.attempt_counter+=1
            if self.attempt_counter<3:
                logging.info("Attempt #"+str(self.attempt_counter)+" Failed loading "+str(path)+" from SmartHsitory "+str(e))
                return self.load_resource()
            else:
                raise SmartHistoryLoadException("After attempt #"+str(self.attempt_counter) +"Failed loading "+str(path)+" from SmartHsitory "+str(e)) 
            # self.response.out.write("error="+e)
                return      
        
        #load the response headers into a dictionary as layer_cache was throwing an error caching an object of class mimetools.Message   
        response_headers={}
        for h in response.headers:
            if h!="Content-Length" and h!="Host":
                response_headers[h]=response.headers[h]
     
        #check to see if it is an image, if so store it in blobstore, set the appropriate headers and remove data from the output
        if(response.headers.get("content-type").find("image")!=-1):
            # Create the file
            file_name = files.blobstore.create(mime_type=response.headers.get("content-type"),_blobinfo_uploaded_filename=SMARTHISTORY_URL+path)
    
            # Open the file and write to it
            with files.open(file_name, 'a') as f:
                f.write(data)
    
            # Finalize the file. Do this before attempting to read it.
            files.finalize(file_name)
    
            # Get the file's blob key
            blob_key = files.blobstore.get_blob_key(file_name)
            
            response_headers["Cache-Control"]="public, max-age="+str(SMARTHISTORY_IMAGE_CACHE_EXPIRATION)+";"
            return ("", response_headers, blob_key)
            
        return [data, response_headers, None]
   
   
