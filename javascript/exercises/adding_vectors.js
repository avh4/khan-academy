// Adding vectors
// Author: Marcia Lee
// Date: 2011-04-21
//
// Video spec:
//  http://vimeo.com/22678065
// Problem speclet:
//  What is a + b? (where the i, j components are non-zero #'s between -10 and 10)
//  Hints: You can either sum i, j components or solve graphically.
//

function AddingVectorsExercise() {
    var a = {name: "\\vec{a}"};
    var b = {name: "\\vec{b}"};
    var sum = {name: "\\vec{c}", x: 20, y: 20};
    var a_color = getNextColor();
    var b_color = getNextColor();
    var sum_color = "#000";
    var a_color_tag = outputColorTag(a_color);
    var b_color_tag = outputColorTag(b_color);
    var end_tag = "</span>";
    var i_hat = "\\hat{i}";
    var j_hat = "\\hat{j}";
	var origin = [0, 0];
    
    generateProblem();
    generateHints();
    
    function generateProblem() {
        a.x = get_random();
        a.y = get_random();
        
        while(isOutOfBounds(sum)) {
            b.x = get_random();
            b.y = get_random();

            sum.x = a.x + b.x;
            sum.y = a.y + b.y;            
        }

        write_text("What is `" + a.name + " + " + b.name + "`?");
        write_text(a_color_tag + "`" + a.name + " = " + outputVector(a) + end_tag);
        write_text(b_color_tag + "`" + b.name + " = " + outputVector(b) + "`" + end_tag);
        
        setCorrectAnswer(outputVector(sum));
        var wrong = {x: a.x + a.y, y: a.y + b.y};
        addWrongChoice(outputVector(wrong));
        
        wrong.x = a.x + b.x;
        wrong.y = a.x + a.y;
        addWrongChoice(outputVector(wrong));
        
        wrong.x = a.x + b.x;
        wrong.y = (-1) * (b.x + b.y);
        addWrongChoice(outputVector(wrong));
        
        wrong.x = a.y + b.y;
        wrong.y = a.x + a.y;
        addWrongChoice(outputVector(wrong));
        
        while(Exercise.getNumPossibleAnswers() < 5) {
            wrong.x = get_random();
            wrong.y = get_random();
            addWrongChoice(outputVector(wrong));
        }
    }
    
    function generateHints() {
        write_step("There are two ways to approach this problem.");
        write_step("1) Sum the `" + i_hat + "` and `" + j_hat + "` components.");
        write_step("2) Solve this graphically.")
        write_step("` " + a.name + " + " + b.name 
                    + " = ( `" + a_color_tag + "`" + a.x + "`" + end_tag + b_color_tag + "`" + format_constant(b.x) + "`" + end_tag + "`)``" + i_hat 
                    + " + ( `" + a_color_tag + "`" + a.y + "`" + end_tag + b_color_tag + "`" + format_constant(b.y) + "`" + end_tag +" `)``" + j_hat + "`");
        write_step("` = " + outputVector(sum) + "`");
    }
    
    this.showProblem = function() {
        this.graph = present;
    	initPlane();

    	present.fontsize = "15";
    	present.fontfamily = "sans-serif";
    	present.fontstyle = "bold";
    	present.marker = "arrow";
	
    	present.stroke = a_color;
    	var a_coord = [a.x, a.y];
        present.line(origin, a_coord);
        present.text(a_coord, "a");
        
        var b_coord = [b.x, b.y];
        present.stroke = b_color;
        present.line(origin, b_coord);
        present.text(b_coord, "b");
    }
    
    this.showGraphHints = function(hint_num) {
        switch(hint_num) {
            case 3:
                var sum_coord = [sum.x, sum.y];
                present.line([a.x, a.y], sum_coord);
                break;
            case 4:
                present.stroke = sum_color;
                present.line(origin, [sum.x, sum.y]);
                break;
            default:
        }
    }
    
    function isOutOfBounds(vector) {
        return vector.x >=10 || vector.x <= -10 || vector.y >= 10 || vector.y <= -10;
    }
    
    function outputVector(v) {
        var i = format_first_coefficient(v.x);
        var j = format_coefficient(v.y);
        if (v.x) {
            i += i_hat;
            j = format_coefficient(v.y);
        } else {
            i = "";
            j = format_first_coefficient(v.y);
        }
            
        if (v.y)
            j += j_hat;
        else
            j = "";            
            
        if (!i && !j)
            j = "0";

        return i + j;
    }
    
    function outputColorTag(color) {
        return "<span style='color: " + color + "'>";
    }
}
