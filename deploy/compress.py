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

def compress_all_javascript():
    dict_packages = packages.javascript
    compress_all_packages(os.path.join("..", "javascript"), dict_packages, ".js")

def compress_all_stylesheets():
    dict_packages = packages.stylesheets
    compress_all_packages(os.path.join("..", "stylesheets"), dict_packages, ".css")

# Combine all .js\.css files in all "-package" suffixed directories
# into a single combined.js\.css file for each package, then
# minify into a single compressed.js\.css file.
def compress_all_packages(default_path, dict_packages, suffix):
    for package_name in dict_packages:
        package = dict_packages[package_name]

        if 'files' in package:
            package_path = package.get("base_path")
            if not package_path:
                dir_name = "%s-package" % package_name
                package_path = os.path.join(default_path, dir_name)

            package_path = os.path.join(os.path.dirname(__file__), package_path)

            compress_package(package_name, package_path, package["files"], suffix)

            hashed_content = "javascript=%s\nstylesheets=%s\n" % \
                (str(packages_javascript), str(packages_stylesheets))
            with open(PATH_PACKAGES_TEMP, "w") as f:
                f.write(hashed_content)

            shutil.move(PATH_PACKAGES_TEMP, PATH_PACKAGES)

    with open(PATH_PACKAGES_HASH, 'w') as hash_file:
        hash_file.write('hashes = %s\n' % str(hashes))

# Overview:
# Take a set of js or css files then:
# 1. Combine them into one large file
# 2. If they are non-mobile css files, replace images where directed to,
#    possibly creating another file
# For each file:
# 3. Hash the file
# 4. Check the hash to see if we already have a copy of the file, stop if we do
# 5. Insert the hash into packages_hash.py
# 6. Compress the file
# 7. Hash the file again
# 8. Create a new file using the hash in its name
# 9. Insert the hash into packages.py and packages_hash.py
#
# Note: The two hashes will be different. The reason we hash twice is because
# we use the first hash in packages_hash.py to check if we need to compress the
# file and the second hash to identify the created file.
# packages_hash file format: 
#     hashes = {'file': (combined hash, compressed hash, final path), ...}
def compress_package(name, path, files, suffix):
    if not os.path.exists(path):
        raise Exception("Path does not exist: %s" % path)

    # Remove the old combined and minified files then replace them
    remove_combined(path, suffix)
    path_combined = combine_package(path, files, suffix)
    remove_compressed(path, suffix)

    with open(path_combined, 'r') as compressed:
        content = compressed.read()
    new_hash = md5.new(content).hexdigest()

    fullname = name+suffix
    if fullname not in hashes \
            or hashes[fullname][0] != new_hash \
            or not os.path.exists(hashes[fullname][2]):

        path_compressed = minify_package(path, path_combined, suffix)
        path_hashed, hash_sig = hash_package(name, path, path_compressed, suffix)

        insert_hash_sig(name, hash_sig, suffix)

        if not os.path.exists(path_hashed):
            raise Exception("Did not successfully compress and hash: %s" % path)

        hashes[fullname] = new_hash, hash_sig, path_hashed
    else:
        insert_hash_sig(name, hashes[fullname][1], suffix)

    if suffix == '.css' and 'mobile' not in name:
        non_ie_fullname = name + '-non-ie' + suffix
        path_with_uris = remove_images(path, path_compressed, suffix)

        with open(path_with_uris, 'r') as imagesremoved:
            content = imagesremoved.read()
        new_hash = md5.new(content).hexdigest()

        if non_ie_fullname not in hashes \
                or hashes[non_ie_fullname][0] != new_hash \
                or not os.path.exists(hashes[non_ie_fullname][2]):

            path_hashed, hash_sig = hash_package(name, path, path_with_uris, suffix)

            insert_hash_sig(name+'-non-ie', hash_sig, suffix)

            if not os.path.exists(path_hashed):
                raise Exception("Did not successfully compress and hash: %s" % \
                    path)

            hashes[non_ie_fullname] = new_hash, hash_sig, path_hashed
        else:
            insert_hash_sig(name+'-non-ie', hashes[non_ie_fullname][1], suffix)

# Remove previous combined.js\.css
def remove_combined(path, suffix):
    filenames = os.listdir(path)
    for filename in filenames:
        if filename.endswith(COMBINED_FILENAME + suffix):
            os.remove(os.path.join(path, filename))

# Remove previous uri.css and compress.js\.css files
def remove_compressed(path, suffix):
    filenames = os.listdir(path)
    for filename in filenames:
        if filename.endswith(URI_FILENAME + suffix) \
                or filename.endswith(COMPRESSED_FILENAME + suffix):
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
            return '\'data:image/%s;base64,%s\''% (ext, base64.b64encode(f.getvalue()))

    return filename

def remove_images(path, path_combined, suffix):
    if suffix != '.css': # don't touch js (yes, this is redundant)
        return path_combined

    path_without_urls = os.path.join(path, URI_FILENAME + suffix)
    print "Replacing urls from %s to get %s" % (path_combined, path_without_urls)

    new_file = open(path_without_urls, 'w')

    r = re.compile('/\*! *data-uri\(\'?/images/(\S+)\.(png|gif|GIF|jpg)\'?\) *\*/')
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
    f = open(path_compressed, "r")
    content = f.read()
    f.close()

    hash_sig = md5.new(content).hexdigest()
    path_hashed = os.path.join(path, "hashed-%s%s" % (hash_sig, suffix))
    
    print "Copying %s into %s" % (path_compressed, path_hashed)
    shutil.copyfile(path_compressed, path_hashed)

    if not os.path.exists(path_hashed):
        raise Exception("Unable to copy to hashed file: %s" % path_compressed)

    return path_hashed, hash_sig

def insert_hash_sig(name, hash_sig, suffix):
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

