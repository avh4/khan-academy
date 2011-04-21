import os
import subprocess

COMBINED_FILENAME = "combined"
COMPRESSED_FILENAME = "compressed"
PACKAGE_SUFFIX = "-package"

# Combine all .js\.css files in all "-package" suffixed directories
# into a single combined.js\.css file for each package, then
# minify into a single compressed.js\.css file.
def compress_all_packages(path, suffix):
    if not os.path.exists(path):
        raise Exception("Path does not exist: %s" % path)

    names = os.listdir(path)
    for name in names:
        if name.endswith(PACKAGE_SUFFIX):
            compress_package(os.path.join(path, name), suffix)

def compress_package(path, suffix):
    if not os.path.exists(path):
        raise Exception("Path does not exist: %s" % path)

    remove_working_files(path, suffix)

    path_combined = combine_package(path, suffix)
    path_compressed = minify_package(path, path_combined, suffix)

    if not os.path.exists(path_compressed):
        raise Exception("Did not successfully compress: %s" % path_compressed)

    return path_compressed

# Remove previous combined.js\.css and compress.js\.css files
def remove_working_files(path, suffix):
    filenames = os.listdir(path)
    for filename in filenames:
        if filename.endswith(COMBINED_FILENAME + suffix) or filename.endswith(COMPRESSED_FILENAME + suffix):
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

# Combine all files into a single combined.js\.css
def combine_package(path, suffix):
    static_filenames = []
    filenames = os.listdir(path)
    for filename in filenames:
        if filename.endswith(suffix):
            static_filenames.append(filename)

    static_filenames = sorted(static_filenames, key=javascript_sort_key)
    path_combined = os.path.join(path, COMBINED_FILENAME + suffix)

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
    f.write(";\n".join(content))
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
    elif filename == "seedrandom.js":
        return 4
    elif filename == "raphael.js":
        return 5
    elif filename == "g.raphael-min.js":
        return 6
    elif filename == "metautil.js":
        return 7
    else:
        return 8

def popen_results(args):
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    return proc.communicate()[0]

