
var Profile = {

    initialGraphUrl: null,
    fLoadingGraph: false,
    fLoadedGraph: false,

    init: function() {
		
		$('.recent-share').hide();
		$('.sharepop').hide();
			
		$(".achievement,.exercise,.video").hover(
			function () {
			    $(this).find(".recent-share").show();
				},
			function () {
			    $(this).find(".recent-share").hide();
				$(this).find(".sharepop").hide();
			  });

		$('.recent-share').click(function() {
		if ( $.browser.msie && (parseInt($.browser.version, 10) < 8) )
			$(this).next(".sharepop").toggle();
		else			
			$(this).next(".sharepop").toggle("drop",{direction:'up'},"fast");	
		return false;
				});
		
        if ($.address)
            $.address.externalChange(function(){ Profile.historyChange(); });

        $(".graph-link").click(function(){Profile.loadGraphFromLink(this); return false;});

        $("#individual_report #achievements #achievement-list > ul li").click(function() {
             var category = $(this).attr('id');
             var clickedBadge = $(this);
             
             $("#badge-container").css("display", "");
             clickedBadge.siblings().removeClass("selected");

             if ($("#badge-container > #" + category ).is(":visible")) {
                if (clickedBadge.parents().hasClass("standard-view")) {
                    $("#badge-container > #" + category ).slideUp(300, function(){
                            $("#badge-container").css("display", "none");
                            clickedBadge.removeClass("selected");
                        });
                }
                else {
                    $("#badge-container > #" + category ).hide();
                    $("#badge-container").css("display", "none");
                    clickedBadge.removeClass("selected");                    
                }
             }
             else {
                var jelContainer = $("#badge-container");
                $(jelContainer).css("min-height", jelContainer.height());
                $(jelContainer).children().hide();
                if (clickedBadge.parents().hasClass("standard-view")) {
                    $("#" + category, jelContainer).slideDown(300, function() {
                        $(jelContainer).animate({"min-height": 0}, 200);
                    });
                } else {
                    $("#" + category, jelContainer).show();
                }
                clickedBadge.addClass("selected");
             }
        });

        $("#stats-nav #nav-accordion").accordion({ header:".header", active:".graph-link-selected", autoHeight: false, clearStyle: true });

        setTimeout(function(){
            if (!Profile.fLoadingGraph && !Profile.fLoadedGraph)
            {
                // If 1000 millis after document.ready fires we still haven't
                // started loading a graph, load manually.
                // The externalChange trigger may have fired before we hooked
                // up a listener.
                Profile.historyChange();
            }
        }, 1000);
    },
	
	
    highlightPoints: function(chart, fxnHighlight) {

        if (!chart) return;

        for (var ix = 0; ix < chart.series.length; ix++) {
            var series = chart.series[ix];

            this.muteSeriesStyles(series);

            for (var ixData = 0; ixData < series.data.length; ixData++) {
                var pointOptions = series.data[ixData].options;
                if (!pointOptions.marker) pointOptions.marker = {};
                pointOptions.marker.enabled = fxnHighlight(pointOptions);
                if (pointOptions.marker.enabled) pointOptions.marker.radius = 6;
            }

            series.isDirty = true;
        }

        chart.redraw();
    },

    muteSeriesStyles: function(series) {
        if (series.options.fMuted) return;

        series.graph.attr('opacity', 0.1);
        series.graph.attr('stroke', '#CCCCCC');
        series.options.lineWidth = 1;
        series.options.shadow = false;
        series.options.fMuted = true;
    },

    accentuateSeriesStyles: function(series) {
        series.options.lineWidth = 3.5;
        series.options.shadow = true;
        series.options.fMuted = false;
    },

    highlightSeries: function(chart, seriesHighlight) {

        if (!chart || !seriesHighlight) return;

        for (var ix = 0; ix < chart.series.length; ix++)
        {
            var series = chart.series[ix];
            var fSelected = (series == seriesHighlight);

            if (series.fSelectedLast == null || series.fSelectedLast != fSelected)
            {
                if (fSelected)
                    this.accentuateSeriesStyles(series);
                else
                    this.muteSeriesStyles(series);

                for (var ixData = 0; ixData < series.data.length; ixData++) {
                    series.data[ixData].options.marker = {
                        enabled: fSelected, 
                        radius: fSelected ? 5 : 4
                    };
                }

                series.isDirty = true;
                series.fSelectedLast = fSelected;
            }
        }

        var options = seriesHighlight.options;
        options.color = '#0080C9';
        seriesHighlight.remove(false);
        chart.addSeries(options, false, false);

        chart.redraw();
    },

    collapseAccordion: function() {
        // Turn on collapsing, collapse everything, and turn off collapsing
        $("#stats-nav #nav-accordion").accordion(
                "option", "collapsible", true).accordion(
                    "activate", false).accordion(
                        "option", "collapsible", false);
    },

    baseGraphHref: function(href) {

        var ixProtocol = href.indexOf("://");
        if (ixProtocol > -1)
            href = href.substring(ixProtocol + "://".length);

        var ixSlash = href.indexOf("/");
        if (ixSlash > -1)
            href = href.substring(href.indexOf("/"));

        var ixQuestionMark = href.indexOf("?");
        if (ixQuestionMark > -1)
            href = href.substring(0, ixQuestionMark);

        return href;
    },

    expandAccordionForHref: function(href) {
        if (!href) return;

        href = this.baseGraphHref(href);

        href = href.replace(/[<>']/g, "");
        var selectorAccordionSection = ".graph-link-header[href*='" + href + "']";
        if ($(selectorAccordionSection).length)
            $("#stats-nav #nav-accordion").accordion("activate", selectorAccordionSection);
        else
            this.collapseAccordion();
    },

    styleSublinkFromHref: function(href) {

        if (!href) return;

        var reDtStart = /dt_start=[^&]+/;

        var matchStart = href.match(reDtStart);
        var sDtStart = matchStart ? matchStart[0] : "dt_start=lastweek";

        href = href.replace(/[<>']/g, "");

        $(".graph-sub-link").removeClass("graph-sub-link-selected");
        $(".graph-sub-link[href*='" + this.baseGraphHref(href) + "'][href*='" + sDtStart + "']").addClass("graph-sub-link-selected");
    },
    
    // called whenever user clicks graph type accordion
    loadGraphFromLink: function(el) {
        if (!el) return;
        Profile.loadGraphStudentListAware(el.href);
    },
    
    loadGraphStudentListAware: function(url) {
        var $dropdown = $('#studentlists_dropdown ol');
        if ($dropdown.length == 1) {
            var list_id = $dropdown.data('selected').key;
            var qs = this.parseQueryString(url);
            if (list_id != 'allstudents')
                qs['list_id'] = list_id;
            else
                delete qs['list_id'];
        
            url = this.baseGraphHref(url) + '?' + this.reconstructQueryString(qs);
        }
        
        this.loadGraph(url);
    },

    loadGraph: function(href, fNoHistoryEntry) {
        if (!href) return;

        if (this.fLoadingGraph) {
            setTimeout(function(){Profile.loadGraph(href);}, 200);
            return;
        }

        this.styleSublinkFromHref(href);
        this.fLoadingGraph = true;
        this.fLoadedGraph = true;

        $.ajax({type: "GET",
                url: Timezone.append_tz_offset_query_param(href),
                data: {},
                success: function(data){ Profile.finishLoadGraph(data, href, fNoHistoryEntry); },
                error: function() { Profile.finishLoadGraphError(); }
        });
        $("#graph-content").html("");
        this.showGraphThrobber(true);
    },

    finishLoadGraph: function(data, href, fNoHistoryEntry) {

        this.fLoadingGraph = false;

        try { eval("var dict_json = " + data); }
        catch(e) { this.finishLoadGraphError(); return; }

        if (!fNoHistoryEntry)
        {
            // Add history entry for browser
            if ($.address)
                $.address.parameter("graph_url", href, false);
        }

        this.showGraphThrobber(false);
        this.styleSublinkFromHref(dict_json.url);
        $("#graph-content").html(dict_json.html);
    },

    finishLoadGraphError: function() {
        this.fLoadingGraph = false;
        this.showGraphThrobber(false);
        $("#graph-content").html("<div class='graph-notification'>It's our fault. We ran into a problem loading this graph. Try again later, and if this continues to happen please <a href='/reportissue?type=Defect'>let us know</a>.</div>");
    },

    historyChange: function(e) {
        var href = ($.address ? $.address.parameter("graph_url") : "") || this.initialGraphUrl;
        if (href)
        {
            this.expandAccordionForHref(href);
            this.loadGraph(href, true);
        }
    },

    showGraphThrobber: function(fVisible) {
        if (fVisible)
            $("#graph-progress-bar").progressbar({value: 100}).slideDown("fast");
        else
            $("#graph-progress-bar").slideUp("fast");
    },
    
    parseQueryString: function(url) {
        var qs = {};
        var parts = url.split('?');
        if(parts.length == 2) {
            var querystring = parts[1].split('&');
            for(var i = 0; i<querystring.length; i++) {
                var kv = querystring[i].split('=');
                if(kv[0].length > 0) //fix trailing &
                    qs[kv[0]] = kv[1];
            }
        }
        return qs;
    },
    
    reconstructQueryString: function(hash, kvjoin, eljoin) {
        kvjoin = kvjoin || '=';
        eljoin = eljoin || '&';
        qs = [];
        for(var key in hash) {
            if(hash.hasOwnProperty(key))
                qs.push(key + kvjoin + hash[key]);
        }
        return qs.join(eljoin);
    }
};

$(function(){Profile.init();});
