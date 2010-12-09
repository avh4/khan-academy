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

function addAutocompleteMatchToList(list, match, fPlaylist, reMatch) {
    var o = {
                "label": match.title,
                "value": match.url,
                "fPlaylist": fPlaylist
            }

    if (reMatch)
        o.label = o.label.replace(reMatch, "<b>$1</b>");

    list[list.length] = o;
}

function initAutocomplete()
{
    var autocompleteWidget = $("#page_search input").autocomplete({
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
                    for (var ix = 0; ix < data.playlists.length; ix++)
                    {
                        addAutocompleteMatchToList(matches, data.playlists[ix], true, reMatch);
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
            window.location = ui.item.value;
            return false;
        },
        open: function(e, ui) {
            var jelMenu = $(autocompleteWidget.data("autocomplete").menu.element);
            var jelInput = $(this);

            var pxRightMenu = jelMenu.offset().left + jelMenu.outerWidth();
            var pxRightInput = jelInput.offset().left + jelInput.outerWidth();

            if (pxRightMenu > pxRightInput)
            {
                // Keep right side of search input and autocomplete menu aligned
                jelMenu.offset({
                                    left: pxRightInput - jelMenu.outerWidth(), 
                                    top: jelMenu.offset().top
                                });
            }
        }
    }).bind("keydown.autocomplete", function(e) {
        if (e.keyCode == $.ui.keyCode.ENTER || e.keyCode == $.ui.keyCode.NUMPAD_ENTER)
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

function onYouTubePlayerReady(playerID) {
    var player = document.getElementById("idPlayer");
    if (!player) player = document.getElementById("idOVideo");

    Discussion.player = player;
    VideoStats.player = player;
}

function onYouTubePlayerStateChange(state) {
    VideoStats.playerStateChange(state);
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
    fWindowHasFocus: false,

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

        var duration = this.player.getDuration() || 0
        if (duration <= 0) return 0;

        return this.getSecondsWatched() / duration;
    },

    startLoggingProgress: function() {

        this.dPercentLastSaved = 0;
        this.cachedDuration = 0;
        this.cachedCurrentTime = 0;
        this.dtSinceSave = new Date();

        this.fWindowHasFocus = true;
        $(window).focus(function(){ VideoStats.fWindowHasFocus = true; });
        $(window).blur(function(){ VideoStats.fWindowHasFocus = false; });

        // Listen to state changes in player to detect final end of video
        this.listenToPlayerStateChange();

        if (!this.fIntervalStarted)
        {
            // Every 10 seconds check to see if we've crossed over our percent
            // granularity logging boundary
            setInterval(function(){VideoStats.saveIfChanged();}, 10000);
            this.fIntervalStarted = true;
        }
    },

    listenToPlayerStateChange: function() {
        if (this.player)
        {
            if (!this.fAlternativePlayer && !this.player.fStateChangeHookAttached)
            {
                // YouTube player is ready, add event listener
                this.player.addEventListener("onStateChange", "onYouTubePlayerStateChange");

                // Multiple calls should be idempotent
                this.player.fStateChangeHookAttached = true;
            }
        }
        else
        {
            // YouTube player isn't ready yet, try again soon
            setTimeout(function(){VideoStats.listenToPlayerStateChange();}, 1000);
        }
    },

    playerStateChange: function(state) {
        // YouTube's "ended" state
        if (state == 0)
        {
            this.saveIfChanged();
        }
    },

    saveIfChanged: function() {

        if (!this.fWindowHasFocus)
        {
            // Only save current stats if the video viewing window has focus
            return;
        }

        var percent = this.getPercentWatched();
        if (percent > this.dPercentLastSaved && 
                (percent > (this.dPercentLastSaved + this.dPercentGranularity) || percent >= 0.99))
        {
            // Either video was finished or another 10% has been watched
            this.save();
        }

    },

    save: function() {

        if (this.fSaving) return;

        this.fSaving = true;
        var percent = this.getPercentWatched();

        $.post("/logvideoprogress", 
                {
                    video_key: $("#video_key").val(),
                    last_second_watched: this.getSecondsWatched(),
                    seconds_watched: this.getSecondsWatchedRestrictedByPageTime()
                },
                function (data) { VideoStats.finishSave(data, percent); });

        this.dtSinceSave = new Date();
    },

    finishSave: function(data, percent) {
        VideoStats.fSaving = false;
        VideoStats.dPercentLastSaved = percent;

        try { eval("var dict_json = " + data); }
        catch(e) { return; }

        if (dict_json.video_points && dict_json.points)
        {
            var jelPoints = $(".video-energy-points");
            jelPoints.attr("title", jelPoints.attr("title").replace(/^\d+/, dict_json.video_points));
            $(".video-energy-points-current", jelPoints).text(dict_json.video_points);
            $("#page_top_nav .energy-points-badge").text(dict_json.points);
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

        if (window.KnowledgeMap)
        {
            $(".exercise-badge").hover(
                    function(){KnowledgeMap.onBadgeMouseover.apply(this);}, 
                    function(){KnowledgeMap.onBadgeMouseout.apply(this);}
            );
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
        var jel = $("#dashboard-drawer, #dashboard-map");
        var yTop = jel.offset().top;
        jel.height($(window).height() - yTop - $("#footer").height() - 20);

        if (window.KnowledgeMap && KnowledgeMap.map)
            google.maps.event.trigger(KnowledgeMap.map, 'resize');
    }
}
