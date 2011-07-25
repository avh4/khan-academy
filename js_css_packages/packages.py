javascript = {
    "shared": {
        "hashed-filename": "hashed-@shared@.js", # @content@ will be replaced with hash by deploy script
        "files": [
            "jquery.js",
            "jquery-ui.js",
            "jquery.ui.menu.js",
            "jquery.watermark.js",
            "jquery.placeholder.js",
            "pageutil.js",
            "api.js",
			"social.js",
        ]
    },
    "video": {
        "hashed-filename": "hashed-@video@.js", # @content@ will be replaced with hash by deploy script
        "files": [
            "video.js",
            "discussion.js",
            "jquery.qtip.js",
        ]
    },
    "homepage": {
        "hashed-filename": "hashed-@homepage@.js", # @content@ will be replaced with hash by deploy script
        "files": [
            "jquery.easing.1.3.js",
            "jquery.cycle.all.min.js",
            "waypoints.min.js",
            "homepage.js",
        ]
    },
    "profile": {
        "hashed-filename": "hashed-@profile@.js", # @content@ will be replaced with hash by deploy script
        "files": [
            "jquery.address-1.4.min.js",
            "highcharts.js",
            "profile.js",
        ]
    },
    "maps": {
        "hashed-filename": "hashed-@maps@.js", # @content@ will be replaced with hash by deploy script
        "files": [
            "fastmarkeroverlay.js",
            "knowledgemap.js",
        ]
    },
    "mobile": {
        "hashed-filename": "hashed-@mobile@.js", # @content@ will be replaced with hash by deploy script
        "files": [
            "jquery.js",
            "jquery.mobile-1.0a4.1.js",
            "iscroll-lite.min.js",
        ]
    },
    "studentlists": {
        "hashed-filename": "hashed-@studentlists@.js", # @content@ will be replaced with hash by deploy script
        "files": [
            "studentlists.js",
            "classprofile.js",
        ]
    },
    "exercises": {
        "hashed-filename": "hashed-@exercises@.js", # @content@ will be replaced with hash by deploy script
        "base_path": "../khan-exercises",
        "base_url": "/khan-exercises",
        "files": [
            "khan-exercise.js",
            "utils/angles.js",
            "utils/answer-types.js",
            "utils/calculus.js",
            "utils/convert-values.js",
            "utils/exponents.js",
            "utils/expressions.js",
            "utils/graphie-helpers.js",
            "utils/graphie.js",
            "utils/kinematics.js",
            "utils/math-format.js",
            "utils/math.js",
            "utils/polynomials.js",
            "utils/probability.js",
            "utils/raphael.js",
            "utils/scratchpad.js",
            "utils/stat.js",
            "utils/tmpl.js",
            "utils/word-problems.js",
        ]
    },
}

stylesheets = {
    "shared": {
        "hashed-filename": "hashed-@shared@.css", # @content@ will be replaced with hash by deploy script
        "files": [
            "default.css",
            "rating.css",
            "stylesheet.css",
            "menu.css",
            "profile.css",
            "museo-sans.css",
            "jquery-ui-1.8.4.custom.css",
        ]
    },
    "mobile": {
        "hashed-filename": "hashed-@mobile@.css", # @content@ will be replaced with hash by deploy script
        "files": [
            "jquery.mobile-1.0a4.1.css",
            "mobile.css",
        ]
    },
    "video": {
        "hashed-filename": "hashed-@video@.css", # @content@ will be replaced with hash by deploy script
        "files": [
            "video.css",
            "discussion.css",
            "jquery.qtip.css",
        ]
    },
    "studentlists": {
        "hashed-filename": "hashed-@studentlists@.css", # @content@ will be replaced with hash by deploy script
        "files": [
            "viewstudentlists.css",
            "viewclassprofile.css",
        ]
    },
}
