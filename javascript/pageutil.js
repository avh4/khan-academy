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
