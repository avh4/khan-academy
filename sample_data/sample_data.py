#!/usr/bin/env python
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

""" Wrapper for uploading/downloading all the system-wide data """

import os
import subprocess
from optparse import OptionParser


def main():
    kinds = ('Exercise', 
             'Video', 
             'Playlist', 
             'ExerciseVideo', 
             'ExercisePlaylist', 
             'VideoPlaylist')
    parser = OptionParser(usage="%prog [options] upload|download", 
                          description="Uploads the sample data to a server or downloads it from the server.  appcfg.py must be in your PATH.")
    parser.add_option("-U", "--url", default="http://localhost:8080/remote_api",
                      help="The location of the remote_api endpoint.")
    parser.add_option("-e", "--email", default="test@example.com",
                      help="The username to use.")
    parser.add_option("-k", "--kinds", default=','.join(kinds),
                      help="The username to use.")
    (options, args) = parser.parse_args()
    if len(args) < 1:
        parser.print_help()
        return
    for kind in options.kinds.split(','):
        filename='%s.data' % kind
        call_args = ['appcfg.py',
                     '--url=%s' % options.url,
                     '--email=%s' % options.email,
                     '--application=khanexercises',
                     '--kind=%s' % kind,
                     '--filename=%s' % filename]
        if options.email == parser.get_option('--email').default:
            call_args.append('--passin')

        if args[0] == 'upload':
            call_args.append('upload_data')
        elif args[0] == 'download':
            if os.path.exists(filename):
                os.remove(filename)
            call_args.append('download_data')
        else:
            parser.print_help()
            return
        print ' '.join(call_args)

        if options.email == parser.get_option('--email').default:
            process = subprocess.Popen(call_args, stdin=subprocess.PIPE)
            # Send a newline for the password prompt
            process.communicate("\n")
        else:
            process = subprocess.Popen(call_args)
        process.wait()

if __name__ == '__main__':
    main()