
var GaeMiniProfiler = {

    display: function(request_id) {
        $.get(
                "/gae_mini_profiler/request_stats",
                { "request_id": request_id },
                function(data) { GaeMiniProfiler.finishDisplay(data); }
        );
    },

    finishDisplay: function(data) {
        console.log(data);
    }

}
