// Derivative Intuition 1
// Author: Marcia Lee
// Date: 2011-05-04
//
// Problem spec: 
//  http://vimeo.com/22658828
// Would be slick to drag the points, but this will do for now.
//

function DerivativeIntuitionExercise() {
    var polynomial;
    var target_slope;
    var x1 = -5;
    var x2 = 5;
    var p1_raphael = null;
    var p2_raphael = null;
    
    
    generateProblem();
    showProblem();
    
    function generateProblem() {
        polynomial = new Polynomial(3);
        var target_x = getRandomIntRange(-7, 7);
        console.log(target_x)
        target_slope = polynomial.evaluateDerivativeAt(target_x);
    }
    
    function showProblem(){
        write_text("Move the red and yellow points to where the derivative is approximately " + target_slope.toFixed(3) + ". ");
        write_text("This module is special in that you can't really get the question wrong -- just keep trying."
                    + " For any point on the blue curve, what is the relationship between the derivative and the tangent line's slope?");
        appendQuestionHtml("<div style=\"clear: both;\"></div>");
        appendQuestionHtml("<div id=\"raphael_container\"></div>");
        RaphaelWrapper.init(500, 500);
        RaphaelWrapper.drawPlane(-10, 10, -10, 10);
        present.stroke = "blue";
        var polyn_str = polynomial.toString();
        present.plot(polyn_str, "graph");
        appendQuestionHtml("<div style=\"font-size: 20px;\">Orange line\'s slope: <span id=\"slope\"></span></div>");
        updateTangent();
    }
    
    this.moveFirst = function(delta) {
        x1 += delta;
        updateTangent();
    }
    
    this.moveSecond = function(delta) {
        x2 += delta;
        updateTangent();
    }
    
    function updateTangent(){
        var p1 = [x1, polynomial.evaluateAt(x1)];
        var p2 = [x2, polynomial.evaluateAt(x2)];
        var mb = pointsToMB(p1, p2);

        present.stroke = "orange";
        present.plot(mb.m + "x + " + mb.b, "tangent");
        
        if (p1_raphael)
            p1_raphael.remove();
        if (p2_raphael)
            p2_raphael.remove();
        p1_raphael = present.ASdot(p1, 3, "yellow", "yellow");
		p2_raphael = present.ASdot(p2, 3, "red", "red");
		$("#slope").html(mb.m.toFixed(3));
		
		if ((Math.abs(mb.m - target_slope) < 0.7) && Math.abs(p1[0] - p2[0]) < 1) {
		    handleCorrectness(true);
            $("#check-answer-results").show();
		} else {
            $("#check-answer-results").hide();
		}
    }
    
    // Given [x1, y1] and [x2, y2], returns {m: m, b: b}
    function pointsToMB(p1, p2) {
        var m = (p2[1] - p1[1]) / (p2[0] - p1[0]);
        var b = p1[1] - (m * p1[0]);
        
        return {m: m, b: b};
    }
}
