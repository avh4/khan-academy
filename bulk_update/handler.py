#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2010, Dean Brettle (dean@brettle.com)
# All rights reserved.
# Licensed under the New BSD License: http://www.opensource.org/licenses/bsd-license.php
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#    * Neither the name of Dean Brettle nor the names of its contributors may be
#      used to endorse or promote products derived from this software without 
#      specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
# POSSIBILITY OF SUCH DAMAGE.

""" A handler that supports updating many entities in the datastore without hitting
request timeout limits.

To use to re-put (i.e. put without changes):

1. Place this file in: /bulk_update/handler.py

2. In your main.py:

import bulk_update.handler

def main():
    application = webapp.WSGIApplication([ 
        ('/admin/reput', bulk_update.handler.UpdateKind),
        ])
    run_wsgi_app(application)

3. Add the following to your app.yaml:
  handlers:
  - url: /admin/.*
    script: main.py
    login: admin
    
4. To re-put (ie. a null update) all the entities of kind ModelClass, visit:
   /admin/reput?kind=ModelClass
   
To actually make changes, add the following in main.py:

class MyUpdateKind(bulk_update.handler.UpdateKind):
    def update(self, entity):
        entity.attr1 = new_value1
        entity.attr2 = new_value2
        ...
        return True

def main():
    application = webapp.WSGIApplication([ 
        ('/admin/myupdate', MyUpdateKind),
        ])
    run_wsgi_app(application)
    
and then visit /admin/myupdate?ModelClass.

"""

import cgi
import datetime
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api.labs import taskqueue
from google.appengine.runtime import DeadlineExceededError

class UpdateKind(webapp.RequestHandler):
    def get(self):
        if not users.is_current_user_admin():
            self.redirect(users.create_login_url(self.request.uri))
            return
        if self.request.get('cancel'):
            self.set_in_progress(False)
            self.response.out.write('Your request to interrupt has been filed.')
        elif self.is_in_progress():
            self.response.out.write('Your request is already in progress.')
        else:
            self.set_in_progress(True)
            taskqueue.add(url=self.request.path, params=self.request.params)
            self.response.out.write('Your request has been added to task queue.  Monitor the log for status updates. ')
            cancel_uri = self.request.path_url + '?' + self.request.query_string + '&cancel=1'
            self.response.out.write('To interrupt the request, <a href="%s">click here</a>.' % cancel_uri)

    def post(self):        
        if not self.is_in_progress():
            logging.info('Cancelled.')
            return
        cursor = self.request.get('cursor')
        count = self.request.get('count')
        if not count:
            count = 0
        count = int(count)
        kind = self.request.get('kind')        
        query = self.get_keys_query(kind)
        if cursor:
            query.with_cursor(cursor)
        done = False
        new_cursor = cursor
        # dev server doesn't throw DeadlineExceededError so we do it ourselves
        deadline = datetime.datetime.now() + datetime.timedelta(seconds=25)
        try:
            for key in query:
                def update_txn():
                    e = db.get(key)
                    if self.update(e):
                        e.put()
                    if datetime.datetime.now() > deadline:
                        raise DeadlineExceededError
                db.run_in_transaction(update_txn)
                new_cursor = query.cursor()
                count = count + 1
            self.set_in_progress(False)
            logging.info('Finished! %d %s processed.', count, kind)
            done = True
        except DeadlineExceededError:
            pass
        except:
            logging.exception('Unexpected exception')
        finally:
            if done:
                return
            if new_cursor == cursor:
                logging.error('Stopped due to lack of progress at %d %s with cursor = %s', count, kind, new_cursor)
                self.set_in_progress(False)
            else:
                logging.info('Processed %d %s so far.  Continuing in a new task...', count, kind)
                new_params = {}
                for name, value in self.request.params.items():
                    new_params[name] = value
                new_params['cursor'] = new_cursor
                new_params['count']= count
                taskqueue.add(url=self.request.path, params=new_params)
                
    def get_memcache_key(self):
        result = self.request.path
        return result
    
    def set_in_progress(self, val):
        memcache.set(self.get_memcache_key(), val)
        
    def is_in_progress(self):
        result = memcache.get(self.get_memcache_key())
        return result
    
    def get_keys_query(self, kind):
        """Returns a keys-only query to get the keys of the entities to update"""
        return db.GqlQuery('select __key__ from %s' % kind)
    
    def update(self, entity):
        """Override in subclasses to make changes to an entity"""
        return True
