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
                        if (result.action_results[el.prop]) {
                            el.fxn(result.action_results[el.prop]);
                        }
                    });
                }
            }
        });
    },

    register: function(prop, fxn) {
        this.hooks[this.hooks.length] = {prop: prop, fxn: fxn};
    }
};

$(function(){ APIActionResults.init(); });

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
            var jelNew = $(sExerciseMessageHtml);
            if (jelNew.children().length) {
                var jel = $("#exercise-message-container");
                jel.empty().append(jelNew.children());

                setTimeout(function(){ jel.slideDown(); }, 50);
            }
        }
    );
});
