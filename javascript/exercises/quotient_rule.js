// Quotient rule
// Author: Omar Rizwan
// Date: 2011-03-08
//
// Problem spec: None
//
// Problem layout:
// d/dx f(x) = ?
// f(x) = 2x^2 + x + 3 (or other function covered in special_derivatives module)

function QuotientRuleExercise() {
    var notation; // notation.fofx = 'y', notation.dfofx = 'dy/dx'

    var top; // top expression
    var bottom; // bottom expression

    var derivative;
    
    this.init = function() {
	generateProblem();
	showProblem();
	generateHints();
    };

    function generateProblem() {
	notation = funcNotation('x');
	
	top = generateFunction('x');
	bottom = generateFunction('x');

	derivative = '(('+bottom.fofx+')('+top.dfofx+') - ('+top.fofx+')('+bottom.dfofx+')) / ' +
	    '(('+bottom.fofx+')^2)';
	
	setCorrectAnswer(derivative);
    }

    function generateHints() {
	write_step('`'+notation.dfofx+' = ((text{bottom})(d/dx text{top}) - (text{top})(d/dx text{bottom}))/(text{bottom}^2)`');

	write_step('`text{bottom} = '+bottom.fofx+'`');
	write_step('`d/dx text{top} = '+top.dfofx+'`');
	write_step('`text{top} = '+top.fofx+'`');
	write_step('`d/dx text{bottom} = '+bottom.dfofx+'`');
	
	write_step('`'+notation.dfofx+' = '+derivative+'`');
    }

    function showProblem() {
	write_text('`'+notation.fofx+' = ('+top.fofx+')/('+bottom.fofx+')`');
	write_text('`'+notation.dfofx+' = ?`');
    }	
}