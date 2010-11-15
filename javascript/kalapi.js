/**
 * DO NOT USE!  This is only psuedocode which *might* be useful in developing a new API for
 * Khan Academy activities/modules.  It is a work-in-progress and does not provide *any* useful
 * functionality at this point. --Dean
 */
ka = {};
ka.activity.sections = {};
ka.activity = {
    init: function() {
        // Find the activity section associated with the current URL.
        // Initialize the activity section.
        // Start the activity section.
    },
    add_section: function(relative_path, section) {
        ka.activity.sections[relative_path] = section;
    }
};
/**
 * Base class for all KA classes
 */
ka.Class = function() { };
ka.Class.prototype = $.extend(new Object, {
    /**
     * Returns the prototype object for the class that is extended.
     */
    base: function() { return this.prototype.prototype; },
    /**
     * Initializes the object based on the optional params argument
     * @param {Object} params
     */
    init: function(params) { this.params = params || {}; }
});

/**
 * A portion of an activity that can be referred to by an URL.
 */
ka.ActivitySection = function() { };
ka.ActivitySection.prototype = $.extend(new ka.Class, {
    /**
     * Initializes an ActivitySection's state from an optional params argument
     * @param {Object} params
     */
    init: function(params){
        this.base().init.apply(this, params);
        if (!this.params.url) 
            this.params.url = window.location.href;
        ka.get_state();
    }
});
ka.Problem = function() { };
ka.Problem.prototype = $.extend(new ka.ActivitySection, {
});
ka.MultipleChoiceProblem = function() { };
ka.MultipleChoiceProblem.prototype = $.extend(new ka.Problem, {
});
ka.Quiz = function() { };
ka.Quiz.prototype = $.extend(new ka.ActivitySection, {     
    init: function(params) {
        var this_quiz = this;
        this.base().init.apply(this, params);
        // Construct the DOM, including a question div and an answer div
        $.get('ka.Quiz.html', function(data) {
           $(document).html(data); 
        });            
        // If there is state stored for this quiz, restore it
        ka.get_state(function(saved_state) {
            this_quiz.params = $.extend(params, { problem_number: 1}, saved_state);
            // Show the current problem.
            var problem = generate_problem(this_quiz.params.problem_number, function() {return this_quiz.get_problem();});
            problem.show();
            // When an answer is provided, evaluate it, log it with the app, and provide feedback
            // If the correct answer is provided, display the next problem, and save the state.
            // When a hint is requested, display it and log it with the app.
        });
    }
});
ka.StreakQuiz = function(params) {
    this.params = params || { required_streak: 10 };
};
ka.StreakQuiz.prototype = $.extend(new ka.Quiz, {
    init: function(params) {
        this.base().init.apply(this, params);
    }
});
