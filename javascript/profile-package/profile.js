
var Profile = {

    initialGraphUrl: null,
    fLoadingGraph: false,
    fLoadedGraph: false,

    init: function() {

        if ($.address)
            $.address.externalChange(function(){ Profile.historyChange(); });

        $(".graph-link").click(function(){Profile.loadGraphFromLink(this); return false;});

        $("#individual_report #achievements #achievement-list > ul li").click(function() {
             var category = $(this).attr('id');
             var clickedBadge = $(this);
             
             $("#badge-container").css("display", "");
             clickedBadge.siblings().removeClass("selected");

             if ($("#badge-container > #" + category ).is(":visible")) {
                $("#badge-container > #" + category ).slideUp(300, function(){
                        $("#badge-container").css("display", "none");
                        clickedBadge.removeClass("selected");
                    });
             }
             else {
                var jelContainer = $("#badge-container");
                $(jelContainer).css("min-height", jelContainer.height());
                $(jelContainer).children().hide();
                $("#" + category, jelContainer).slideDown(300, function() {
                    $(jelContainer).animate({"min-height": 0}, 200);
                });
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

    loadGraphFromLink: function(el) {
        if (!el) return;
        this.loadGraph(el.href);
    },

    loadGraph: function(href, fNoHistoryEntry) {
        if (!href) return;

        if (this.fLoadingGraph) {
            setTimeout(function(){Profile.loadGraph(href);}, 200);
            return;
        }

        this.styleSublinkFromHref(href);
        this.fLoadingGraph = true;

        $.ajax({type: "GET",
                url: Timezone.append_tz_offset_query_param(href),
                data: {},
                success: function(data){ Profile.finishLoadGraph(data, href, fNoHistoryEntry); },
                error: function() { Profile.fLoadingGraph = false;}
        });
        $("#graph-content").html("");
        this.showGraphThrobber(true);
    },

    finishLoadGraph: function(data, href, fNoHistoryEntry) {

        this.fLoadingGraph = false;
        this.fLoadedGraph = true;

        try { eval("var dict_json = " + data); }
        catch(e) { return; }

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
    }
};

$(function(){Profile.init();});
