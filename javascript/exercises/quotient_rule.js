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

    function quotientDerivative(tp, dtp, btm, dbtm) {
	return '(('+btm+')('+dtp+') - ('+tp+')('+dbtm+')) / ' +
	    '(('+btm+')^2)';
    }

    function generateProblem() {
	notation = funcNotation('x');
	
	do {
	    top = generateFunction('x');
	    bottom = generateFunction('x');
	} while (top == bottom); // TODO do expression comparison, this will cover most blatant cases though
	
	derivative = quotientDerivative(top.fofx, top.dfofx, bottom.fofx, bottom.dfofx);
	
	setCorrectAnswer(derivative);

	for (var i = 0; i < 3; i++) {
	    addWrongChoice(quotientDerivative(top.fofx, randomMember(top.wrongs), bottom.fofx, randomMember(bottom.wrongs)));
	}
	addWrongChoice('(('+bottom.fofx+')('+top.dfofx+') + ('+top.fofx+')('+bottom.dfofx+')) / ' +
		       '(('+bottom.fofx+')^2)');
	addWrongChoice('(('+bottom.fofx+')('+top.dfofx+') - ('+top.fofx+')('+bottom.dfofx+')) / ' +
		       '(('+bottom.dfofx+')^2)');
	addWrongChoice('(('+top.fofx+')('+top.dfofx+') + ('+bottom.fofx+')('+bottom.dfofx+')) / ' +
		       '(('+bottom.dfofx+')^2)');
	addWrongChoice('(('+top.fofx+')('+top.dfofx+') - ('+bottom.fofx+')('+bottom.dfofx+')) / ' +
		       '(('+bottom.dfofx+')^2)');
	addWrongChoice('(('+top.fofx+')('+bottom.dfofx+') - ('+bottom.fofx+')('+top.dfofx+')) / ' +
		       '(('+bottom.dfofx+')^2)');
    }

    function generateHints() {
	write_step('<p>We remember from the quotient rule that</p><p>`'+
		   notation.dfofx+' = ((text{bottom})(d/dx text{top}) - (text{top})(d/dx text{bottom}))/(text{bottom}^2)`</p>');

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