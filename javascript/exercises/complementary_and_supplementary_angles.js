var IS_COMP = 0;
var IS_SUPP = 1;

function ComplementarySupplementaryAnglesExercise(t) {
    if (t == undefined)
        t = getRandomIntRange(IS_COMP, IS_SUPP);

    var exercise_type = t;
    var term;
    var total;
    var known_degree;
    
    var horizontal_label;
    var vertical_label;
    var origin_label;
    var vector_label;
    
    var known_label;
    var answer_label;
    
    function generateProblem() {
        if (exercise_type) {
            total = 90;
            term = "complementary";
        } else {
            total = 180;
            term = "supplementary";
        }
        
        horizontal_label = getNextLabel();
        vertical_label = getNextLabel();
        origin_label = getNextLabel();
        vector_label = getNextLabel();
        
        known_degree = getRandomIntRange(1, total-1);
        
        known_label = "`&#8736;" + horizontal_label + origin_label + vector_label + "`";
        answer_label = "`&#8736;" + vector_label + origin_label + vertical_label + "`";
        
        write_text(known_label + " and " + answer_label + " are " + term + ".");
        write_text("If " + known_label + " measures `" + known_degree + "&#176;`, how many degrees is " + answer_label + "?");
        var answer = total - known_degree;
        setCorrectAnswer(total - known_degree);
    }
    
    function generateHints() {
        open_left_padding(30);
        write_step(capitalize(term) + " angles sum to `" + total + "&#176;`.");
        write_step(known_label + " ` + ` " + answer_label + " ` =  " + total + "&#176;`");
        write_step(answer_label + " ` =  " + total + " &#176; -` " + known_label);
        write_step(answer_label + " ` = " + total + " &#176; - " + known_degree + "&#176;`");
        write_step(answer_label + " ` = " + (total - known_degree) + "&#176;`");
        close_left_padding();
    }
    
    generateProblem();
    generateHints();
    
    this.showProblem = function() {
        this.graph = present;
    	present.initPicture(-1.1, 1.1, -1.1, 1.1);
    	present.marker = "arrow";
    	
    	var known_rad = convertDegreeToRadian(known_degree);
        var vector = [Math.cos(known_rad), Math.sin(known_rad)];
        var rotation = getRandomIntRange(0, 360);
        
    	var origin = [0, 0];
    	var horizontal = rotateVector([1, 0], rotation);
    	
    	if (exercise_type)
        	var vertical = rotateVector([0, 1], rotation);
        else
            var vertical = rotateVector([-1, 0], rotation);
        vector = rotateVector(vector, rotation);
        
        present.line(origin, horizontal);
        present.line(origin, vertical);
        present.line(origin, vector);
        
        present.text(origin, origin_label);
        present.text(horizontal, horizontal_label);
        present.text(vertical, vertical_label);
        present.text(vector, vector_label);
    }
    
    function capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
}
