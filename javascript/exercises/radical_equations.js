// Radical Equations
// Author: Marcia Lee
// Date: 2011-03-01
//
// Problem spec:
// http://www.youtube.com/watch?v=Y79NEYvQvW8
//
// Problem layout:
// Solve an equation of the form:  a * sqrt(x) + b = c * sqrt(x) + d
//  Because this problem uses get_random(), 
//  the variables are non-zero integers between -10 and 10.
//  a cannot equal c, but b can equal d.
//
// Conceptually, this builds off of Linear Equations 3, which solves equations of the form ax + b = cx + d.
// 

function RadicalEquationsExercise() {
    var exc;
    var x;
    
    this.init = function() {
        exc = new LinearEquations();
        exc.init("sqrt(x)");
        calculateCorrectAnswer();
        generateWrongAnswers();
    }
    
    function calculateCorrectAnswer() {
        var right_c = exc.getRightConstant();
        var left_x = exc.getLeftCoeff();

	    x = format_fraction(right_c * right_c, left_x * left_x);        
        var correct_answer = '';
        if (right_c / left_x < 0) {
            correct_answer = '`No solution`'
            write_step('The principal root of a number cannot be negative. So, there is no solution.')
		} else {
            var root = format_fraction(right_c, left_x);
            write_step('Squaring both sides, `sqrt(x) * sqrt(x) = (' + root + ') * (' + root + ')`'); 
            
            var correct_answer_backticked = '`x = ' + x + '`';
            write_step('So, '+ correct_answer_backticked);
            
            // setCorrectAnswer wraps the answer in backticks, so let's remove them.
            correct_answer = correct_answer_backticked.replace(/`/gi, '')
   		}

		setCorrectAnswer(correct_answer);
    }
    
    function generateWrongAnswers() {
        addWrongChoice('`No solution`');
        addWrongChoice('x = ' + x);

        var numerator = exc.getRightConstant();
        var denominator = exc.getLeftCoeff();

 		while (Exercise.getNumPossibleAnswers() < 4)
 		{
            var n_shift = get_random();
            var d_shift = get_random();

            while (d_shift+denominator == 0)
                d_shift = get_random();

            var wrong_numerator = numerator + n_shift;
            var wrong_denominator = denominator + d_shift;
            var wrong_answer = format_fraction(wrong_numerator * wrong_numerator, wrong_denominator * wrong_denominator)

            addWrongChoice('x = ' + wrong_answer);
 		}
     }
}

