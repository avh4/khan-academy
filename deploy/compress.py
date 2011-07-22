from __future__ import with_statement
import os
import shutil
import subprocess
import sys
import md5
import re
import StringIO
import base64
import copy
from string import lower

sys.path.append(os.path.abspath("."))
from js_css_packages import packages

COMBINED_FILENAME = "combined"
URI_FILENAME = "uri"
COMPRESSED_FILENAME = "compressed"
PACKAGE_SUFFIX = "-package"
HASHED_FILENAME_PREFIX = "hashed-"
PATH_PACKAGES = "js_css_packages/packages.py"
PATH_PACKAGES_TEMP = "js_css_packages/packages.compresstemp.py"
PATH_PACKAGES_HASH = "js_css_packages/packages_hash.py"

packages_stylesheets = copy.deepcopy(packages.stylesheets)
packages_javascript = copy.deepcopy(packages.javascript)
if os.path.exists(PATH_PACKAGES_HASH):
    import js_css_packages.packages_hash
    hashes = copy.deepcopy(js_css_packages.packages_hash.hashes)
else:
    hashes = {}
    
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
        if 'files' in package:
            dir_name = "%s-package" % package_name
            package_path = os.path.join(path, dir_name)

            compress_package(package_name, package_path, package["files"], suffix)

            hashed_content = "javascript=%s\nstylesheets=%s\n" % \
                (str(packages_javascript), str(packages_stylesheets))
            with open(PATH_PACKAGES_TEMP, "w") as f:
                f.write(hashed_content)

            shutil.move(PATH_PACKAGES_TEMP, PATH_PACKAGES)

    with open(PATH_PACKAGES_HASH, 'w') as hash_file:
        hash_file.write('hashes = %s\n' % str(hashes))

def compress_package(name, path, files, suffix):
    if not os.path.exists(path):
        raise Exception("Path does not exist: %s" % path)

    # Remove the old combined and minified files then replace them
    remove_working_files_1(path, suffix)
    path_combined = combine_package(path, files, suffix)
    path_compressed = minify_package(path, path_combined, suffix)
  
    with open(path_compressed, 'r') as compressed:
        content = compressed.read()
    new_hash = md5.new(content).hexdigest()

    # Good to go if the file (or files) is the same as the previous version
    # (which is still there)
    good_to_go = True

    # If the file's hash is the same we re-insert it into packages.py to be
    # safe, if it's not then we're going to have to re-minify it
    # TODO fix above
    fullname = name+suffix
    if fullname in hashes and hashes[fullname] == new_hash:
        pass#insert_hash_sig(name, new_hash, suffix)
    else:
        good_to_go = False
    hashes[fullname] = new_hash

    if suffix == '.css' and 'mobile' not in name:
        ie_name = name+'-ie'
        ie_fullname = ie_name + suffix
        path_with_uris = remove_images(path, path_compressed, suffix)

        with open(path_with_uris, 'r') as compressed:
            content = compressed.read()
        new_hash = md5.new(content).hexdigest()

        if ie_fullname in hashes and hashes[ie_fullname] == new_hash:
            pass#insert_hash_sig(ie_name, new_hash, suffix)
        else:
            good_to_go = False
        hashes[ie_fullname] = new_hash

    remove_working_files_2(path, suffix)

    if good_to_go:
        return

    # Don't replace images for js and mobile css
    if suffix == '.css' and 'mobile' not in name:
        path_hashed = hash_package(name, path, path_compressed, suffix)

        if not os.path.exists(path_hashed):
            raise Exception("Did not successfully compress and hash: %s" % path)

        suffix = '-ie'+suffix

    path_hashed = hash_package(name, path, path_compressed, suffix)

    if not os.path.exists(path_hashed):
        raise Exception("Did not successfully compress and hash: %s" % path)

# Remove previous combined.js\.css, and compress.js\.css files
def remove_working_files_1(path, suffix):
    filenames = os.listdir(path)
    for filename in filenames:
        if filename.endswith(COMBINED_FILENAME + suffix) \
                or filename.endswith(COMPRESSED_FILENAME + suffix):
            os.remove(os.path.join(path, filename))

# Remove previous hashed-*.js\.css and uri.css
def remove_working_files_2(path, suffix):
    filenames = os.listdir(path)
    for filename in filenames:
        if filename.endswith(URI_FILENAME + suffix) \
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
    filename = filename.group(0)

    ext = os.path.splitext(filename)[1][1:].lower()
    if ext == 'jpg':
        ext = 'jpeg'

    filename = os.path.join(os.path.dirname(__file__), '..', filename[1:])

    print "Removing images from %s" % filename
    if os.path.isfile(filename):
        with open(filename) as img:
            f = StringIO.StringIO()
            f.write(img.read())
            return 'data:image/%s;base64,%s'% (ext, base64.b64encode(f.getvalue()))

    return filename

def remove_images(path, path_combined, suffix):
    if suffix != '.css': # don't touch js (yes, this is redundant)
        return path_combined

    path_without_urls = os.path.join(path, URI_FILENAME + suffix)
    print "Replacing urls from %s to get %s" % (path_combined, path_without_urls)

    new_file = open(path_without_urls, 'w')

    r = re.compile('data-uri\(/images/(\S+)\.(png|gif|GIF|jpg)\)')
    with open(path_combined) as f:
        for line in f:
            if r.search(line):
                for i in r.finditer(line):
                    # /images/dark-page-bg.png
                    #         <----------> <->
                    #             |         |
                    #         i.group(1) i.group(2)
                    urlpath = '/images/'+i.group(1)+'.'+i.group(2)
                    line = re.sub(urlpath, remove_images_from_line, line, 1)
            new_file.write(line)

    new_file.close()

    if not os.path.exists(path_without_urls):
          raise Exception("Unable to remove images: %s" % path_combined)

    return path_without_urls

def hash_package(name, path, path_compressed, suffix):
    print "NAME: %s\n PATH_COMPRESSED: %s\nSUFFIX: %s\n" % (name, path_compressed, suffix)
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
    if suffix == '-ie.css':
        name = name+'-ie'

    print "Inserting %s sig (%s) into %s\n" % (name, hash_sig, PATH_PACKAGES)

    current_dict = packages_stylesheets if suffix.endswith('.css') else packages_javascript
    if name not in current_dict:
        current_dict[name] = {}
    current_dict[name]["hashed-filename"] = "hashed-%s%s" % (hash_sig, suffix)

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

