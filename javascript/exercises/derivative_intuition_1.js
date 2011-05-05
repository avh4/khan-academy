// Derivative Intuition 1
// Author: Marcia Lee
// Date: 2011-05-04
//
// Problem spec: 
//  http://vimeo.com/22658828
//

function DerivativeIntuitionExercise() {
    var polynomial;
    
    generateProblem();
    showProblem();
    generateHints();
    
    function generateProblem() {
        write_text("At which of these x values does the derivative of function graphed below equal ~0.5?");
        appendQuestionHtml("<div style=\"clear: both;\"></div>")
        polynomial = new Polynomial(3);

        setCorrectAnswer("`Answer`");
        
        addWrongChoice("`Acute`");
        addWrongChoice("`Right`");
        addWrongChoice("`Obtuse`");
    }
    
    function generateHints() {
        writeStep("blahblah");
    }
    
    function showProblem(){
        appendQuestionHtml("<div id=\"raphael_container\"></div>");
        RaphaelWrapper.init(500, 500);
        RaphaelWrapper.drawPlane(-10, 10, -10, 10);
        present.stroke = "blue";

        var polyn_str = polynomial.toString();
        present.plot(polyn_str);
    }
}
