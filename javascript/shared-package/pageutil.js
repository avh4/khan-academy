function addCommas(nStr) // to show clean number format for "people learning right now" -- no built in JS function
{
	nStr += '';
	var x = nStr.split('.');
	var x1 = x[0];
	var x2 = x.length > 1 ? '.' + x[1] : '';
	var rgx = /(\d+)(\d{3})/;
	while (rgx.test(x1)) {
		x1 = x1.replace(rgx, '$1' + ',' + '$2');
	}
	return x1 + x2;
}

function validateEmail(sEmail)
{ 
     var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/ 
     return sEmail.match(re) 
}

function addAutocompleteMatchToList(list, match, fPlaylist, reMatch) {
    var o = {
                "label": match.title,
                "title": match.title,
                "value": match.url,
                "key": match.key,
                "fPlaylist": fPlaylist
            }

    if (reMatch)
        o.label = o.label.replace(reMatch, "<b>$1</b>");

    list[list.length] = o;
}

function initAutocomplete(selector, fPlaylists, fxnSelect, fIgnoreSubmitOnEnter)
{
    var autocompleteWidget = $(selector).autocomplete({
        delay: 150,
        source: function(req, fxnCallback) {

            // Get autocomplete matches
            $.getJSON("/autocomplete", {"q": req.term}, function(data) {

                var matches = [];

                if (data != null)
                {
                    var reMatch = null;
                    
                    // Try to find the "scent" of the match.  If regexp fails
                    // to compile for any input reason, ignore.
                    try {
                        reMatch = new RegExp("(" + data.query + ")", "i");
                    }
                    catch(e) {
                        reMatch = null;
                    }

                    // Add playlist and video matches to list of autocomplete suggestions
                    
                    if (fPlaylists)
                    {
                        for (var ix = 0; ix < data.playlists.length; ix++)
                        {
                            addAutocompleteMatchToList(matches, data.playlists[ix], true, reMatch);
                        }
                    }
                    for (var ix = 0; ix < data.videos.length; ix++)
                    {
                        addAutocompleteMatchToList(matches, data.videos[ix], false, reMatch);
                    }
                }

                fxnCallback(matches);

            });
        },
        focus: function() {
            return false;
        },
        select: function(e, ui) {
            if (fxnSelect)
                fxnSelect(ui.item);
            else
                window.location = ui.item.value;
            return false;
        },
        open: function(e, ui) {
            var jelMenu = $(autocompleteWidget.data("autocomplete").menu.element);
            var jelInput = $(this);

            var pxRightMenu = jelMenu.offset().right + jelMenu.outerWidth();
            var pxRightInput = jelInput.offset().right + jelInput.outerWidth();

            if (pxRightMenu > pxRightInput)
            {
                // Keep right side of search input and autocomplete menu aligned
                jelMenu.offset({
                                    right: pxRightInput - jelMenu.outerWidth(), 
                                    top: jelMenu.offset().top
                                });
            }
        }
    }).bind("keydown.autocomplete", function(e) {
        if (!fIgnoreSubmitOnEnter && e.keyCode == $.ui.keyCode.ENTER || e.keyCode == $.ui.keyCode.NUMPAD_ENTER)
        {
            if (!autocompleteWidget.data("autocomplete").selectedItem)
            {
                // If enter is pressed and no item is selected, default autocomplete behavior
                // is to do nothing.  We don't want this behavior, we want to fall back to search.
                $(this.form).submit();
            }
        }
    });

    autocompleteWidget.data("autocomplete")._renderItem = function(ul, item) {
        // Customize the display of autocomplete suggestions
        var jLink = $("<a></a>").html(item.label);
        if (item.fPlaylist)
            jLink.prepend("<span class='playlist'>Playlist </span>");

        return $("<li></li>")
            .data("item.autocomplete", item)
            .append(jLink)
            .appendTo(ul);
        }

     autocompleteWidget.data("autocomplete").menu.select = function(e) {
        // jquery-ui.js's ui.autocomplete widget relies on an implementation of ui.menu
        // that is overridden by our jquery.ui.menu.js.  We need to trigger "selected"
        // here for this specific autocomplete box, not "select."
        this._trigger("selected", e, { item: this.active });
    }
}

$(function(){
    // Configure the search form
    if ($('#page_search input[type=text]').placeholder().length)
        initAutocomplete("#page_search input", true);
});

function createCookie(name,value,days) {
    if (days) {
        var date = new Date();
        date.setTime(date.getTime()+(days*24*60*60*1000));
        var expires = "; expires="+date.toGMTString();
    }
    else var expires = "";
    document.cookie = name+"="+value+expires+"; path=/";
}

function readCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1,c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
    }
    return null;
}

function eraseCookie(name) {
    createCookie(name,"",-1);
}

function onYouTubePlayerStateChange(state) {
    VideoStats.playerStateChange(state);
}

var VideoControls = {

    player: null,

    initJumpLinks: function() {
        $("span.youTube").addClass("playYouTube").removeClass("youTube").click(VideoControls.clickYouTubeJump);
    },

    clickYouTubeJump: function() {
        var seconds = $(this).attr("seconds");
        if (VideoControls.player && seconds)
        {
            VideoControls.player.seekTo(Math.max(0, seconds - 2), true);
            VideoControls.scrollToPlayer();
        }
    },

    play: function() {
        if (VideoControls.player && VideoControls.player.playVideo)
            VideoControls.player.playVideo();
    },

    pause: function() {
        if (VideoControls.player && VideoControls.player.pauseVideo)
            VideoControls.player.pauseVideo();
    },

    scrollToPlayer: function() {
        // If user has scrolled below the youtube video, scroll to top of video
        // when a play link is clicked.
        var yTop = $(VideoControls.player).offset().top - 2;
        if ($(window).scrollTop() > yTop) $(window).scrollTop(yTop);
    },

    initThumbnails: function() {

        var jelThumbnails = $("#thumbnails");

        jelThumbnails.cycle({ 
            fx:     'scrollHorz', 
            timeout: 0,
            speed: 550,
            slideResize: 0,
            easing: 'backinout',
            startingSlide: 0,
            prev: '#arrow-left',
            next: '#arrow-right'
        });

        // We want #thumbnails to be full width even though the cycle plugin doesn't
        jelThumbnails.css({ width: "" });

        $(".thumbnail_link", jelThumbnails).click(VideoControls.thumbnailClick);
    },

    thumbnailClick: function() {
        var jelParent = $(this).parents("td").first();
        var youtubeId = jelParent.attr("data-youtube-id");
        if (VideoControls.player && youtubeId)
        {
            VideoControls.player.loadVideoById(youtubeId, 0, "default");
            VideoControls.scrollToPlayer();
            $("#thumbnails td.selected").removeClass("selected");
            jelParent.addClass("selected");
            return false;
        }
    }
}

var VideoStats = {

    dPercentGranularity: 0.05,
    dPercentLastSaved: 0.0,
    fSaving: false,
    player: null,
    fIntervalStarted: false,
    fAlternativePlayer: false,
    cachedDuration: 0, // For use by alternative FLV player
    cachedCurrentTime: 0, // For use by alternative FLV player
    dtSinceSave: null,

    getSecondsWatched: function() {
        if (!this.player) return 0;
        return this.player.getCurrentTime() || 0;
    },

    getSecondsWatchedRestrictedByPageTime: function() {
        var secondsPageTime = ((new Date()) - this.dtSinceSave) / 1000.0;
        return Math.min(secondsPageTime, this.getSecondsWatched());
    },

    getPercentWatched: function() {
        if (!this.player) return 0;

        var duration = this.player.getDuration() || 0;
        if (duration <= 0) return 0;

        return this.getSecondsWatched() / duration;
    },

    startLoggingProgress: function() {

        this.dPercentLastSaved = 0;
        this.cachedDuration = 0;
        this.cachedCurrentTime = 0;
        this.dtSinceSave = new Date();

        // Listen to state changes in player to detect final end of video
        if (this.player) this.listenToPlayerStateChange();
        // If the player isn't ready yet or if it is replaced in the future,
        // listen to the state changes once it is ready/replaced.
        var me = this;
        $(this).bind("playerready", function() {
            me.listenToPlayerStateChange();
        });

        if (!this.fIntervalStarted)
        {
            // Every 10 seconds check to see if we've crossed over our percent
            // granularity logging boundary
            setInterval(function(){VideoStats.playerStateChange(-2);}, 10000);
            this.fIntervalStarted = true;
        }
    },

    listenToPlayerStateChange: function() {
        if (!this.fAlternativePlayer && !this.player.fStateChangeHookAttached)
        {
            // YouTube player is ready, add event listener
            this.player.addEventListener("onStateChange", "onYouTubePlayerStateChange");

            // Multiple calls should be idempotent
            this.player.fStateChangeHookAttached = true;
        }
    },

    playerStateChange: function(state) {
        if (state == -2) { // playing normally
            var percent = this.getPercentWatched();
            if (percent > (this.dPercentLastSaved + this.dPercentGranularity))
            {
                // Another 10% has been watched
                this.save();
            }
        } else if (state == 0) { // ended
            this.save();
        } else if (state == 2) { // paused
            if (this.getSecondsWatchedRestrictedByPageTime() > 1) {
              this.save();
            }
        } else if (state == 1) { // play
            this.dtSinceSave = new Date();
        }
        // If state is buffering, unstarted, or cued, don't do anything
    },

    save: function() {

        if (this.fSaving) return;

        this.fSaving = true;
        var percent = this.getPercentWatched();
        var dtSinceSaveBeforeError = this.dtSinceSave;

        $.ajax({type: "GET",
                url: "/logvideoprogress", 
                data: {
                    video_key: $(".video_key_primary").val(),
                    last_second_watched: this.getSecondsWatched(),
                    seconds_watched: this.getSecondsWatchedRestrictedByPageTime()
                },
                success: function (data) { VideoStats.finishSave(data, percent); },
                error: function () {
                    // Restore pre-error stats so user can still get full
                    // credit for video even if GAE timed out on a request
                    VideoStats.fSaving = false; VideoStats.dtSinceSave = dtSinceSaveBeforeError;
                }
        });

        this.dtSinceSave = new Date();
    },

    /* Use qtip2 (http://craigsworks.com/projects/qtip2/) to create a tooltip
     * that looks like the ones on youtube.
     *
     * Example: 
     * VideoStats.tooltip('#points-badge-hover', '0 of 500 points');
     */
    tooltip: function(selector, content) {
        $(selector).qtip({
            content: {
                text: content
            },
            style: {
                classes: 'ui-tooltip-youtube'
            },
            position: {
                my: 'top center',
                at: 'bottom center'
            },
            hide: {
                fixed: true,
                delay: 150
            }
        });
    },

    finishSave: function(data, percent) {
        VideoStats.fSaving = false;
        VideoStats.dPercentLastSaved = percent;

        try { eval("var dict_json = " + data); }
        catch(e) { return; }

        if (dict_json.video_points && dict_json.user_points_html)
        {
            // Update the energy points box with the new data.
            var jelPoints = $(".video-energy-points");
            jelPoints.data("title", jelPoints.data("title").replace(/^\d+/, dict_json.video_points));
            $(".video-energy-points-current", jelPoints).text(dict_json.video_points);
            $("#user-points-container").html(dict_json.user_points_html);

            // Replace the old tooltip with an updated one.
            VideoStats.tooltip('#points-badge-hover', jelPoints.data('title'));
        }
    },

    prepareAlternativePlayer: function() {

        this.player = $("#flvPlayer").get(0);
        if (!this.player) return;

        // Simulate the necessary YouTube APIs for the alternative player
        this.player.getDuration = function() { return VideoStats.cachedDuration; };
        this.player.getCurrentTime = function() { return VideoStats.cachedCurrentTime; };

        this.fAlternativePlayer = true;
    },

    cacheStats: function(time, duration) {

        // Only update current time if it exists, not if video finished
        // and scrubber went back to 0.
        var currentTime = parseFloat(time);
        if (currentTime) this.cachedCurrentTime = currentTime;

        this.cachedDuration = parseFloat(duration);
    }
};

function onYouTubePlayerReady(playerID) {
    // Ensure UniSub widget will know about ready players if/when it loads.
    (window.unisubs_readyAPIIDs = window.unisubs_readyAPIIDs || []).push((playerID == "undefined" || !playerID) ? '' : playerID);

    var player = null;
    if (!player) player = $(".mirosubs-widget object").get(0);
    if (!player) player = document.getElementById("idPlayer");
    if (!player) player = document.getElementById("idOVideo");

    VideoControls.player = player;
    VideoStats.player = player;
    // The UniSub (aka mirosubs) widget replaces the YouTube player with a copy 
    // and that will cause onYouTubePlayerReady() to be called again.  So, we trigger 
    // 'playerready' events on any objects that are using the player so that they can 
    // take appropriate action to use the new player.
    $(VideoControls).trigger('playerready');
    $(VideoStats).trigger('playerready');
}

var Drawer = {

    init: function() {

        $('#show-all-exercises').click(function() {Drawer.toggleAllExercises(); return false;});

        $('#dashboard-drawer .exercise-badge').click( function() {
            window.location = $(".exercise-title a", this).attr("href");
            return false;
        });
        
        $('.toggle-drawer').click(function() {Drawer.toggle(); return false;});

        $(window).resize(function(){Drawer.resize();});
        this.resize();

        if (window.iScroll)
        {
            // Mobile device, support single-finger touch scrolling
            $("#dashboard-drawer").removeClass("drawer-hoverable");
            var scroller = new iScroll('dashboard-drawer-inner', { hScroll: false, hScrollbar: false, vScrollbar: false });
        }
        else
        {
            if (window.KnowledgeMap)
            {
                $(".exercise-badge").hover(
                        function(){KnowledgeMap.onBadgeMouseover.apply(this);}, 
                        function(){KnowledgeMap.onBadgeMouseout.apply(this);}
                );
            }
        }
    },

    toggleAllExercises: function() {

        var fVisible = $('#all-exercises').is(':visible');

        if (fVisible)
        {
            $('#all-exercises').slideUp(500);
            $('#show-all-exercises').html('Show All');
        }
        else
        {
            $('#all-exercises').slideDown(500);
            $('#show-all-exercises').html('Hide All');
        }

        $.post("/saveexpandedallexercises", {
            "expanded": fVisible ? "0" : "1"
        }); // Fire and forget
    },

    isExpanded: function() {
        var sCSSLeft = $("#dashboard-drawer").css("left").toLowerCase();
        return sCSSLeft == "0px" || sCSSLeft == "auto" || sCSSLeft == "";
    },

    toggle: function() {

        if (this.fToggling) return;

        var fExpanded = this.isExpanded();

        var jelDrawer = $("#dashboard-drawer");
        var leftDrawer = fExpanded ? -1 * (jelDrawer.width() + 20) : 0;
        
        var jelTitle = $("#dashboard-title");
        var leftTitle = fExpanded ? -1 * (jelTitle.width() +10 ): 5;
        
        jelTitle.animate({left: leftTitle}, 500);

        this.fToggling = true;
        jelDrawer.animate({left: leftDrawer}, 500, function() {Drawer.fToggling = false;});

        if (window.KnowledgeMap)
        {
            var leftMap = (fExpanded ? 0 : 340);
            $("#map-canvas").animate({marginRight: leftMap + "px", left: leftMap + "px"}, 
                    500,
                    function() {
                        google.maps.event.trigger(KnowledgeMap.map, 'resize');
                    }
            );
        }
    },

    resize: function() {
        var jel = $("#dashboard-drawer, #dashboard-drawer-inner, #dashboard-map");
        var jelDrawerInner = $("#dashboard-drawer-inner");
        var yTop = jel.offset().top;
        jel.height($(window).height() - yTop - $("#footer").height());
        // Account for padding in the dashboard drawer
        jelDrawerInner.height(jelDrawerInner.height() - 20);

        if (window.KnowledgeMap && KnowledgeMap.map)
            google.maps.event.trigger(KnowledgeMap.map, 'resize');
    }
}

var Badges = {

    show: function(sBadgeContainerHtml) {
        var jel = $(".badge-award-container");

        if (sBadgeContainerHtml)
        {
            jel.remove();
            $("body").append(sBadgeContainerHtml);
            jel = $(".badge-award-container");

            if (jel.length) Social.init(jel);
        }

        if (!jel.length) return;

        $(".achievement-badge", jel).click(function(){
            window.location = "/badges/view";
            return false;
        });

        var jelTarget = $(".badge-target");
        var top = jelTarget.offset().top + jelTarget.height() + 5;

        setTimeout(function(){
            jel.css("visibility", "hidden").css("display", "");
            jel.css("left", jelTarget.offset().left + jelTarget.width() - jel.width()).css("top", -1 * jel.height());
            var topBounce = top + 10;
            jel.css("display", "").css("visibility", "visible");
            jel.animate({top: topBounce}, 300, function(){jel.animate({top: top}, 100);});
        }, 100);
    },

    hide: function() {
        var jel = $(".badge-award-container");
        jel.animate({top: -1 * jel.height()}, 500, function(){jel.hide();});
    },

    showMoreContext: function(el) {
        var jelLink = $(el).parents(".badge-context-hidden-link");
        var jelBadge = jelLink.parents(".achievement-badge")
        var jelContext = $(".badge-context-hidden", jelBadge);

        if (jelLink.length && jelBadge.length && jelContext.length)
        {
            $(".ellipsis", jelLink).remove();
            jelLink.html(jelLink.text());
            jelContext.css("display", "");
            jelBadge.css("min-height", jelBadge.css("height")).css("height", "auto");
            jelBadge.nextAll(".achievement-badge").first().css("clear", "both");
        }
    }
}

var Notifications = {

    show: function(sNotificationContainerHtml) {
        var jel = $(".notification-bar");

        if (sNotificationContainerHtml)
        {
            var jelNew = $(sNotificationContainerHtml);
            jel.empty().append(jelNew.children());
        }

        $(".notification-bar-close").click(function(){
            Notifications.hide();
            return false;
        });

        if (!jel.is(":visible")) {
            setTimeout(function(){
                
                jel
                    .css("visibility", "hidden")
                    .css("display", "")
                    .css("top",-1*jel.height())
                    .css("visibility", "visible");

                // Queue:false to make sure all of these run at the same time
                var animationOptions = {duration: 350, queue: false};
                
                $("body").animate({ backgroundPosition: "0px 35px" }, animationOptions);
                $("header").animate({ paddingTop: 35 }, animationOptions);
                jel.show().animate({ top: 0 }, animationOptions);

            }, 100);
        }
    },

    hide: function() {
        var jel = $(".notification-bar");

        // Queue:false to make sure all of these run at the same time
        var animationOptions = {duration: 350, queue: false};
        
        $("body").animate({ backgroundPosition: "0px 0px" }, animationOptions);
        $("header").animate({ paddingTop: 0 }, animationOptions);
        jel.animate(
                { top: -1 * jel.height() }, 
                $.extend(animationOptions, 
                    { complete: function(){ jel.remove(); } }
                )
        );

        $.post("/notifierclose"); 
    }
}

var Timezone = {
    tz_offset: null,

    append_tz_offset_query_param: function(href) {
        if (href.indexOf("?") > -1)
            href += "&";
        else
            href += "?";
        return href + "tz_offset=" + Timezone.get_tz_offset();
    },

    get_tz_offset: function() {
        if (this.tz_offset == null)
            this.tz_offset = -1 * (new Date()).getTimezoneOffset();
        return this.tz_offset;
    }
}

var MailingList = {
    init: function(sIdList) {
        var jelMailingListContainer = $("#mailing_list_container_" + sIdList);
        var jelMailingList = $("form", jelMailingListContainer);
        var jelEmail = $(".email", jelMailingList);

        jelEmail.placeholder().change(function(){
            $(".error", jelMailingListContainer).css("display", (!$(this).val() || validateEmail($(this).val())) ? "none" : "");
        }).keypress(function(){
            if ($(".error", jelMailingListContainer).is(":visible") && validateEmail($(this).val()))
                $(".error", jelMailingListContainer).css("display", "none");
        });

        jelMailingList.submit(function(e){
            if (validateEmail(jelEmail.val()))
            {
                $.post("/mailing-lists/subscribe", {list_id: sIdList, email: jelEmail.val()});
                jelMailingListContainer.html("Done!");
            }
            e.preventDefault();
            return false;
        });
    }
}

var CSSMenus = {

    active_menu: null,

    init: function() {
        // Make the CSS-only menus click-activated
        $('.noscript').removeClass('noscript');
        $('.css-menu > ul > li').click(function() {
            if (CSSMenus.active_menu) CSSMenus.active_menu.removeClass('css-menu-js-hover');

            if (CSSMenus.active_menu && this == CSSMenus.active_menu[0])
                CSSMenus.active_menu = null;
            else
                CSSMenus.active_menu = $(this).addClass('css-menu-js-hover');
        });

        $(document).bind("click focusin", function(e){
            if (CSSMenus.active_menu && $(e.target).closest(".css-menu").length == 0) {
                CSSMenus.active_menu.removeClass('css-menu-js-hover');
                CSSMenus.active_menu = null;
            }
        });

        // Make the CSS-only menus keyboard-accessible
        $('.css-menu a').focus(function(e){
            $(e.target).addClass('css-menu-js-hover').closest(".css-menu > ul > li").addClass('css-menu-js-hover');
        }).blur(function(e){
            $(e.target).removeClass('css-menu-js-hover').closest(".css-menu > ul > li").removeClass('css-menu-js-hover');
        });
    }
}
$(CSSMenus.init);

var IEHtml5 = {
    init: function() {
        // Create a dummy version of each HTML5 element we use so that IE 6-8 can style them.
        var html5elements = ['header', 'footer', 'nav', 'article', 'section', 'menu'];
        for (var i = 0; i < html5elements.length; i++) {
            document.createElement(html5elements[i]);
        }
   }
}
IEHtml5.init();

var VideoViews = {
    init: function() {
        var seedTime = new Date(2011,3,22);  //Seed Date is set to October 31, 2010  0-January, 11-december
        var seedTotalViews = 50397618;
        var seedDailyViews = 170000;

        var currentTime = new Date();
        var secondsSince = (currentTime.getTime()-seedTime.getTime())/1000;
        var viewsPerSecond = seedDailyViews/24/3600
        var estimatedTotalViews = Math.round(seedTotalViews + secondsSince*viewsPerSecond)

        var totalViewsString = addCommas(""+estimatedTotalViews);

        $('#page_num_visitors').append(totalViewsString);
        $('#page_visitors').css('display', 'inline');
    }
}
$(VideoViews.init);

var FacebookHook = {
    init: function() {
        if (!window.FB_APP_ID) return;

        window.fbAsyncInit = function() {
            FB.init({appId: FB_APP_ID, status: true, cookie: true, xfbml: true});

            if (!USERNAME) {
                FB.Event.subscribe('auth.login', function(response) {
                    if (URL_CONTINUE)
                        window.location = URL_CONTINUE;
                    else
                        window.location.reload();
               });
            }

            FB.getLoginStatus(function(response) {
                if (response.session) {
                    $('#page_logout').click(function(e) {
                        FB.logout(function() { 
                            window.location = $("#page_logout").attr("href"); 
                        });
                        e.preventDefault();
                        return false;
                    });
                }
            });
        };

        $(function() {
            var e = document.createElement('script'); e.async = true;
            e.src = document.location.protocol + '//connect.facebook.net/en_US/all.js';
            document.getElementById('fb-root').appendChild(e);
        }); 
    }
}
FacebookHook.init();

var Throbber = {
    jElement: null,

    show: function(jTarget, fOnLeft) {
        if (!Throbber.jElement)
        {
            Throbber.jElement = $("<img style='display:none;' src='/images/throbber.gif' class='throbber'/>");
            $(document.body).append(Throbber.jElement);
        }

        if (!jTarget.length) return;

        var offset = jTarget.offset();

        var top = offset.top + (jTarget.height() / 2) - 8;
        var left = fOnLeft ? (offset.left - 16 - 4) : (offset.left + jTarget.width() + 4);

        Throbber.jElement.css("top", top).css("left", left).css("display", "");
    },

    hide: function() {
        if (Throbber.jElement) Throbber.jElement.css("display", "none");
    }
};
