import os
import subprocess

COMBINED_FILENAME = "combined.js"
COMPRESSED_FILENAME = "compressed.js"
PACKAGE_SUFFIX = "-package"

# Combine all .js files in all "-package" suffixed directories
# into a single combined.js file for each package, then
# minify into a single compressed.js file.
def compress_all_js_packages(path):
    if not os.path.exists(path):
        raise Exception("Path does not exist: %s" % path)

    names = os.listdir(path)
    for name in names:
        if name.endswith(PACKAGE_SUFFIX):
            compress_js(os.path.join(path, name))

def compress_js(path):
    if not os.path.exists(path):
        raise Exception("Path does not exist: %s" % path)

    remove_working_files(path)

    path_combined = combine_js(path)
    path_compressed = minify_js(path, path_combined)

    if not os.path.exists(path_compressed):
        raise Exception("Did not successfully compress: %s" % path_compressed)

    return path_compressed

# Remove previous combined.js and compress.js files
def remove_working_files(path):
    filenames = os.listdir(path)
    for filename in filenames:
        if filename.endswith(COMBINED_FILENAME) or filename.endswith(COMPRESSED_FILENAME):
            os.remove(os.path.join(path, filename))

# Use YUICompressor to minify the combined file
def minify_js(path, path_combined):
    path_compressed = os.path.join(path, COMPRESSED_FILENAME)

    print "Compressing %s into %s" % (path_combined, path_compressed)
    print popen_results(["java", "-jar", "yuicompressor-2.4.2.jar", "--charset", "utf-8", path_combined, "-o", path_compressed])
    
    if not os.path.exists(path_compressed):
        raise Exception("Unable to YUICompress: %s" % path_combined)

    return path_compressed

# Combine all files into a single combined.js
def combine_js(path):
    static_filenames = []
    filenames = os.listdir(path)
    for filename in filenames:
        if filename.endswith(".js"):
            static_filenames.append(filename)

    static_filenames = sorted(static_filenames, key=javascript_sort_key)
    path_combined = os.path.join(path, COMBINED_FILENAME)

    print "Building %s" % path_combined

    content = []
    for static_filename in static_filenames:
        path_static = os.path.join(path, static_filename)
        print "   ...adding %s" % path_static
        f = open(path_static, 'r')
        content.append(f.read())
        f.close()

    if os.path.exists(path_combined):
        raise Exception("File about to be compressed already exists: %s" % path_combined)

    f = open(path_combined, "w")
    f.write("\n".join(content))
    f.close()

    return path_combined

# Make sure jQuery or other necessary components are sent down at top of any file.
# We shouldn't need to add to this list if we only run JS code using jQuery's $(fxn) 
# standard for document.ready.
def javascript_sort_key(filename):
    if filename == "jquery.js":
        return 0
    elif filename == "jquery-ui.js":
        return 1
    elif filename.startswith("jquery."):
        return 2
    elif filename == "metautil.js":
        return 3
    else:
        return 4

def popen_results(args):
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    return proc.communicate()[0]

