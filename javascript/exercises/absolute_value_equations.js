// Absolute Value Equations
// Author: Marcia Lee
// Date: 2011-02-23
//
// Problem spec:
// http://www.youtube.com/watch?v=pIDDD68fC-M
//
// Problem layout:
// Solve an equation of the form:  a|x| + b = c|x| + d
//  Because this problem uses get_random(), 
//  the variables are non-zero integers between -10 and 10.
//  a cannot equal c, but b can equal d.
//
// Conceptually, this builds off of Linear Equations 3, which solves equations of the form ax + b = cx + d.
// 

function AbsoluteValueEquationsExercise() {
    var exc = new LinearEquations();
    exc.init("|x|");
    calculateCorrectAnswer();
    generateWrongAnswers();
    
    function calculateCorrectAnswer() {
        var right_c = exc.getRightConstant();
        var left_x = exc.getLeftCoeff();
        
        var correct_answer = '';
        if (right_c / left_x < 0) {
            correct_answer = '`No solution`'
            write_step('The absolute value can never be negative. So, there is no solution.')
        } else {
		    var x = format_fraction(Math.abs(right_c), Math.abs(left_x))
		    if (right_c == 0)
		        correct_answer_backticked = '`x = 0`'
		    else
                correct_answer_backticked = '`x = - ' + x + '` or `x = ' + x + '`';

            write_step('So, the correct answer is ' + correct_answer_backticked)
            
            // setCorrectAnswer wraps the answer in backticks, so let's remove them.
            correct_answer = correct_answer_backticked.replace(/`/gi, '')
   		}

		setCorrectAnswer(correct_answer);
    }
    
    function generateWrongAnswers() {
        if (get_random() > 0)
            addWrongChoice('`No solution`')

        var numerator = exc.getRightConstant();
        var denominator = exc.getLeftCoeff();

		while (Exercise.getNumPossibleAnswers() < 4)
		{
    			var n_shift = get_random();
    			var d_shift = get_random();

    			while (d_shift+denominator == 0)
    				d_shift = get_random();

    			var wrong_numerator = Math.abs(numerator + n_shift)
    			var wrong_denominator = Math.abs(denominator + d_shift)
    			var wrong_answer = format_fraction(wrong_numerator, wrong_denominator)
    			
    			if (wrong_answer == 0)
    			    addWrongChoice('x = 0');
    			else
    			    addWrongChoice('x = - ' + wrong_answer + ' or x = ' + wrong_answer);               
		}
	}
}

