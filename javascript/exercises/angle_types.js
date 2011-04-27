// Angle types
// Author: Marcia Lee
// Date: 2011-03-29
//
// Problem speclet:
//  Is this an acute, right, or obtuse angle?
//  The angle drawn has measure in [10, 75], [105, 170], or is exactly 90.
//  The angle is rotated randomly, to make this exercise a little bit more interesting.
//

function AngleTypesExercise() {
    generateProblem();
    showProblem();
    generateHints();
    
    function generateProblem() {
        write_text("Is this an acute, right, or obtuse angle?");
        var answer = "";
        
        switch (getRandomIntRange(0, 2)) {
            case 0:
                this.measure = getRandomIntRange(10, 75);
                this.hint = "Because this angle measures less than 90 degrees, it is an acute angle.";
                answer = "`Acute`";
                break;
            case 1:
                this.measure = getRandomIntRange(105, 170);
                this.hint = "Because this angle measures more than 90 degrees, it is an obtuse angle.";
                answer = "`Obtuse`";
                break;
            default:
                this.measure = 90;
                this.hint = "Because this angle measures exactly 90 degrees, it is a right angle";
                answer = "`Right`";
        }
    
        setCorrectAnswer(answer);
        
        addWrongChoice("`Acute`");
        addWrongChoice("`Right`");
        addWrongChoice("`Obtuse`");
    }
    
    function generateHints() {
        open_left_padding(30);
        writeStep("Acute angles measure less than 90 degrees.");
        writeStep("Right angles measure exactly 90 degrees.");
        writeStep("Obtuse angles measure more than 90 degrees.");
        close_left_padding();
        writeStep(this.hint);
    }
    
    function showProblem(){
    	present.initPicture(-1, 1, -1, 1);
    	present.marker = "arrow";
    	
    	var rotation = getRandomIntRange(0, 360);
    	
    	measure = convertDegreeToRadian(measure);
    	rotation = convertDegreeToRadian(rotation);
    	
    	var x = Math.cos(measure) * Math.cos(rotation) - Math.sin(measure) * Math.sin(rotation);
    	var y = Math.cos(measure) * Math.sin(rotation) + Math.sin(measure) * Math.cos(rotation);
        present.line([0, 0], [x, y]);
        present.line([0, 0], [Math.cos(rotation), Math.sin(rotation)]);
    }
}
