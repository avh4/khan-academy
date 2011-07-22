var APIActionResults = {

    init: function() {
        this.hooks = [];

        $(document).ajaxComplete(function (e, xhr, settings) {

            if (xhr && 
                xhr.getResponseHeader('X-KA-API-Response') && 
                xhr.responseText) {

                try { eval("var result = " + xhr.responseText); }
                catch(e) { return; }

                if (result && result.action_results) {
                    $(APIActionResults.hooks).each(function(ix, el) {
                        if (typeof result.action_results[el.prop] !== "undefined") {
                            el.fxn(result.action_results[el.prop]);
                        }
                    });
                }
            }
        });

        jQuery.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (settings && settings.url && settings.url.indexOf("/api/") > -1) {
                    if (fkey) {
                        // Send xsrf token along via header so it can be matched up
                        // w/ cookie value.
                        xhr.setRequestHeader("X_KA_FKEY", fkey);
                    }
                }
            }
        });

    },

    register: function(prop, fxn) {
        this.hooks[this.hooks.length] = {prop: prop, fxn: fxn};
    }
};

APIActionResults.init();

// Show any badges that were awarded w/ any API ajax request
$(function(){ APIActionResults.register("badges_earned_html", Badges.show); });

// Show any login notifications that pop up w/ any API ajax request
$(function(){ APIActionResults.register("login_notifications_html", Notifications.show); });

// Update user info after appropriate API ajax requests
$(function(){ APIActionResults.register("user_info_html", 
        function(sUserInfoHtml) {
            $("#user-info").html(sUserInfoHtml);
        }
    );
});

// Update exercise message after appropriate API ajax requests
$(function(){ APIActionResults.register("exercise_message_html", 
        function(sExerciseMessageHtml) {
            var jel = $("#exercise-message-container");
            var jelNew = $(sExerciseMessageHtml);
            if (jelNew.children().length) {
                jel.empty().append(jelNew.children());
                setTimeout(function(){ jel.slideDown(); }, 50);
            }
            else {
                jel.slideUp();
            }
        }
    );
});

// Update exercise icons after appropriate API ajax requests
$(function(){ APIActionResults.register("exercise_states", 
        function(dictExerciseStates) {
            var sPrefix = dictExerciseStates.summative ? "node-challenge" : "node";
            var src = "";

            if (dictExerciseStates.review)
                src = "/images/node-review.png";
            else if (dictExerciseStates.suggested)
                src = "/images/" + sPrefix + "-suggested.png";
            else if (dictExerciseStates.proficient)
                src = "/images/" + sPrefix + "-complete.png";
            else
                src = "/images/" + sPrefix + "-not-started.png";

            $("#exercise-icon-container img").attr("src", src);
        }
    );
});
