var Homepage = {

    active_menu: null,

    init: function() {
        VideoControls.initThumbnails();

        // Make the CSS-only menus click-activated
        $('.noscript').removeClass('noscript');
        $('.css-menu > ul > li').click(function() {
            if (Homepage.active_menu) Homepage.active_menu.removeClass('css-menu-js-hover');

            if (Homepage.active_menu && this == Homepage.active_menu[0])
                Homepage.active_menu = null;
            else
                Homepage.active_menu = $(this).addClass('css-menu-js-hover');
        });
        $(document).bind("click focusin", function(e){
            if ($(e.target).closest(".css-menu").length == 0 && Homepage.active_menu) {
                Homepage.active_menu.removeClass('css-menu-js-hover');
                Homepage.active_menu = null;
            }
        });
        // Make the CSS-only menus keyboard-accessible
        $('.css-menu a').focus(function(e){
            $(e.target).addClass('css-menu-js-hover').closest(".css-menu > ul > li").addClass('css-menu-js-hover');
        }).blur(function(e){
            $(e.target).removeClass('css-menu-js-hover').closest(".css-menu > ul > li").removeClass('css-menu-js-hover');
        });

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

            if (!Homepage.fTopBound)
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
        if (Homepage.active_menu) Homepage.active_menu.removeClass('css-menu-js-hover');
    }
}

$(function(){Homepage.init();});

