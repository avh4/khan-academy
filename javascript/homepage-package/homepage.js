var Homepage = {

    init: function() {
        VideoControls.initThumbnails();
        Homepage.initWaypoints();
    },

    initWaypoints: function() {

        // Waypoint behavior not supported in IE7-
        if ($.browser.msie && parseInt($.browser.version) < 8) return;

        $.waypoints.settings.scrollThrottle = 50;

        $("#browse").waypoint(function(event, direction) {

            var jel = $(this);
            var jelFixed = $("#browse-fixed")
            var jelTop = $("#back-to-top");

            jelTop.click(function(){Homepage.waypointTop(jel, jelFixed, jelTop);});

            if (direction == "down")
                Homepage.waypointVideos(jel, jelFixed, jelTop);
            else
                Homepage.waypointTop(jel, jelFixed, jelTop);
        });
    },

    waypointTop: function(jel, jelFixed, jelTop) {
        jelFixed.css("display", "none");
        if (!$.browser.msie) jelTop.css("display", "none");
    },

    waypointVideos: function(jel, jelFixed, jelTop) {
        jelFixed.css("width", jel.width()).css("display", "block");
        if (!$.browser.msie) jelTop.css("display", "block");
        if (CSSMenus.active_menu) CSSMenus.active_menu.removeClass('css-menu-js-hover');
    }
}

$(function(){Homepage.init();});

