from __future__ import with_statement
import os
import shutil
import subprocess
import sys
import md5
import re
import StringIO
import base64

sys.path.append(os.path.abspath("."))
from js_css_packages import packages

COMBINED_FILENAME = "combined"
URI_FILENAME = "uri"
COMPRESSED_FILENAME = "compressed"
PACKAGE_SUFFIX = "-package"
HASHED_FILENAME_PREFIX = "hashed-"
PATH_PACKAGES = "js_css_packages/packages.py"
PATH_PACKAGES_TEMP = "js_css_packages/packages.compresstemp.py"

def revert_js_css_hashes():
    print "Reverting %s" % PATH_PACKAGES
    popen_results(['hg', 'revert', PATH_PACKAGES])

def compress_all_javascript(path):
    dict_packages = packages.javascript
    compress_all_packages(path, dict_packages, ".js")

def compress_all_stylesheets(path):
    dict_packages = packages.stylesheets
    compress_all_packages(path, dict_packages, ".css")

# Combine all .js\.css files in all "-package" suffixed directories
# into a single combined.js\.css file for each package, then
# minify into a single compressed.js\.css file.
def compress_all_packages(path, dict_packages, suffix):
    if not os.path.exists(path):
        raise Exception("Path does not exist: %s" % path)

    for package_name in dict_packages:
        package = dict_packages[package_name]

        dir_name = "%s-package" % package_name
        package_path = os.path.join(path, dir_name)

        compress_package(package_name, package_path, package["files"], suffix)

def compress_package(name, path, files, suffix):
    if not os.path.exists(path):
        raise Exception("Path does not exist: %s" % path)

    remove_working_files(path, suffix)

    path_combined = combine_package(path, files, suffix)
    path_with_uris = remove_urls(path, path_combined, suffix)
    path_compressed = minify_package(path, path_combined, suffix)
    path_hashed = hash_package(name, path, path_compressed, suffix)

    if not os.path.exists(path_hashed):
        raise Exception("Did not successfully compress and hash: %s" % path)

    return path_hashed

# Remove previous combined.js\.css and compress.js\.css files
def remove_working_files(path, suffix):
    filenames = os.listdir(path)
    for filename in filenames:
        if filename.endswith(COMBINED_FILENAME + suffix) \
                or filename.endswith(COMPRESSED_FILENAME + suffix) \
                or filename.startswith(HASHED_FILENAME_PREFIX):
            os.remove(os.path.join(path, filename))

# Use YUICompressor to minify the combined file
def minify_package(path, path_combined, suffix):
    path_compressed = os.path.join(path, COMPRESSED_FILENAME + suffix)
    path_compressor = os.path.join(os.path.dirname(__file__), "yuicompressor-2.4.2.jar")

    print "Compressing %s into %s" % (path_combined, path_compressed)
    print popen_results(["java", "-jar", path_compressor, "--charset", "utf-8", path_combined, "-o", path_compressed])
    
    if not os.path.exists(path_compressed):
        raise Exception("Unable to YUICompress: %s" % path_combined)

    return path_compressed

def remove_images_from_line(filename):
    filename = filename.group(0) # open image
    filename = os.path.join('..', filename[1:])
    print "filename: %s" % filename
    if os.path.isfile(filename):
        with open(filename) as img:
            f = StringIO.StringIO()
            f.write(img.read())
            data = 'data:image/png;base64,'+base64.b64encode(f.getvalue())
            print data
            return data
            #return 'data:image/png;base64,'+base64.b64encode(f.getvalue())

    return filename

def remove_urls(path, path_combined, suffix):
    if suffix != '.css':
        return path_combined

    path_without_urls = os.path.join(path, URI_FILENAME + suffix)
    print "Replacing urls from %s to get %s" % (path_combined, path_without_urls)

    r = re.compile('replace-with-data-uri\(/images/(\S+)\.(png|gif|GIF|jpg)\)')
    with open(path_combined) as f:
        for line in f:
            if r.search(line):
                for i in r.finditer(line):
                    urlpath = '/images/'+i.group(1)+'.'+i.group(2)
                    print "urlpath: %s" % urlpath
                    re.sub(urlpath, remove_images_from_line, line, 1)

    if not os.path.exists(path_without_urls):
          raise Exception("Unable to remove images: %s" % path_combined)

    return path_without_urls

def hash_package(name, path, path_compressed, suffix):
    f = open(path_compressed, "r")
    content = f.read()
    f.close()

    hash_sig = md5.new(content).hexdigest()
    path_hashed = os.path.join(path, "hashed-%s%s" % (hash_sig, suffix))
    
    print "Copying %s into %s" % (path_compressed, path_hashed)
    shutil.copyfile(path_compressed, path_hashed)

    if not os.path.exists(path_hashed):
        raise Exception("Unable to copy to hashed file: %s" % path_compressed)

    insert_hash_sig(name, hash_sig, suffix)

    return path_hashed

def insert_hash_sig(name, hash_sig, suffix):
    print "Inserting %s sig (%s) into %s\n" % (name, hash_sig, PATH_PACKAGES)

    f = open(PATH_PACKAGES, "r")
    content = f.read()
    f.close()

    re_search = "@%s@%s" % (name, suffix)
    re_replace = "%s%s" % (hash_sig, suffix)
    hashed_content = re.sub(re_search, re_replace, content)

    if content == hashed_content:
        raise Exception("Hash sig insertion failed: %s" % name)

    f = open(PATH_PACKAGES_TEMP, "w")
    f.write(hashed_content)
    f.close()

    shutil.move(PATH_PACKAGES_TEMP, PATH_PACKAGES)

# Combine all files into a single combined.js\.css
def combine_package(path, files, suffix):
    path_combined = os.path.join(path, COMBINED_FILENAME + suffix)

    print "Building %s" % path_combined

    content = []
    for static_filename in files:
        path_static = os.path.join(path, static_filename)
        print "   ...adding %s" % path_static
        f = open(path_static, 'r')
        content.append(f.read())
        f.close()

    if os.path.exists(path_combined):
        raise Exception("File about to be compressed already exists: %s" % path_combined)

    f = open(path_combined, "w")
    separator = "\n" if suffix.endswith(".css") else ";\n"
    f.write(separator.join(content))
    f.close()

    return path_combined

def popen_results(args):
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    return proc.communicate()[0]

