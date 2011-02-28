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
// Literally, this is a skeletal version of Linear Equations 1.
// 


function AbsoluteValueEquationsExercise() {
    var left_x = [get_random()]; 
    var right_x = [get_random()];
    var left_c = [get_random()];
    var right_c = [get_random()];
    
    this.init = function() {
        while (right_x[0] == left_x[0])
        	right_x[0] = get_random();

        showProblem();    
        generateHints();
        calculateCorrectAnswer();
        generateWrongAnswers();
    }
    
    function showProblem() {
        write_text("Solve for `x`:");
        
        var lhs = format_expression(left_x, ' |x| ', noSelColor, true) + format_expression(left_c, '', noSelColor, false)
        var rhs = format_expression(right_x, ' |x| ', noSelColor, true) + format_expression(right_c, '', noSelColor, false)
        
		table_step_header('', lhs, rhs);
    }
    
    function generateHints() {
        addXTerm();                 // Add -c|x| to both sides
		addConstant();              // Add -b
        multiplyCoefficient();      // Multiply by 1/a
    }
    
    function addXTerm() {
		var term = format_first_coefficient(Math.abs(right_x[0])) + ' |x| ';
		var term_html = format_string_with_color(term, selColor);
		
        var step = generateHint(right_x[0], term_html);
		var lhs = step.lhs_term + format_expression(left_x, ' |x| ', noSelColor, false) + format_expression(left_c, '', noSelColor, false);
		var rhs = format_expression(right_x, ' |x| ', noSelColor, true) + format_expression(right_c, '', noSelColor, false) + step.rhs_term;
		write_table_step(step.explanation, lhs, rhs);

        var explanation = format_expression([-1 * right_x[0], left_x[0]], ' |x| ', selColor, true)
        explanation += format_string_with_color('=', selColor) + format_expression([left_x[0]-right_x[0]], ' |x| ', selColor, true)
        
		explanation += '; ';
		explanation += format_expression([right_x[0],-1*right_x[0]], ' |x| ', selColor, true) + format_string_with_color('=0', selColor);
		
		left_x = [left_x[0]-right_x[0]];
		right_x = [];
		
        lhs = format_expression(left_x, ' |x| ', selColor, true) + format_expression(left_c, '', noSelColor, false)
        rhs =  format_expression(right_c, '', noSelColor, true)

		write_table_step(explanation, lhs, rhs);
    }
    
    function addConstant() {
		var term = Math.abs(left_c[0]);
    	var term_html = format_string_with_color(term, selColor);
    	
    	var step = generateHint(left_c[0], term_html)
    	
        var lhs = step.lhs_term + format_expression(left_x, ' |x| ', noSelColor, false)
                    + format_expression(left_c, '', noSelColor, false)
        
		var rhs = format_expression(right_c, '', noSelColor, true) + step.rhs_term;
		write_table_step(step.explanation, lhs, rhs);

        var explanation = format_expression([-1*left_c[0],left_c[0]], '', selColor, true);
        explanation += format_string_with_color('=0', selColor);
		explanation += '; ';
		explanation += format_expression([right_c[0],-1*left_c[0]], '', selColor, true)
		explanation += format_string_with_color('=', selColor)
		explanation += format_expression([right_c[0]-left_c[0]], '', selColor, true)
		
		right_c = [right_c[0]-left_c[0]];
		left_c = [];
		
        lhs = format_expression(left_x, ' |x| ', noSelColor, true)
        rhs = format_expression(right_c, '', selColor, true)
		write_table_step(explanation, lhs, rhs)
    }
    
    function generateHint(value, term_html) {
        var hint = {};
        if (value > 0) {
            hint.explanation = 'Subtract ' + term_html + ' from both sides';
		    hint.lhs_term =format_string_with_color('-', selColor) + term_html;
		    hint.rhs_term = format_string_with_color('-', selColor) + term_html;
		} else {
		    hint.explanation = 'Add ' + term_html + ' to both sides';
		    hint.lhs_term = term_html;
		    hint.rhs_term = format_string_with_color('+', selColor) + term_html;
		}
        return hint;
    }
    
    function multiplyCoefficient() {
        var term = format_fraction(1, left_x[0]);
		var term_html = format_string_with_color('(' + term + ')', selColor);
		var explanation = 'Multiply both sides by '+ term_html + '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;';
		
		var lhs = term_html + '`*`'+format_expression(left_x, ' |x| ', noSelColor, true);
		var rhs = format_expression(right_c, '', noSelColor, true)+'`*`' + term_html;
		write_table_step(explanation, lhs, rhs);
		
		explanation = "Simplify.";
		write_table_step(explanation, ' |x| ', format_fraction(right_c[0], left_x[0]));

		table_step_footer();
    }
    
    function calculateCorrectAnswer() {
        var correct_answer = '';
        if (right_c[0] / left_x[0] < 0) {
            correct_answer = '`No solution`'
            write_step('The absolute value can never be negative. So, there is no solution.')
		} else {
		    var x = format_fraction(Math.abs(right_c[0]), Math.abs(left_x[0]))
		    if (x == 0)
		        correct_answer_backticked = '`x=0`'
		    else
                correct_answer_backticked = '`x= - ' + x + '` or `x=' + x + '`';

            write_step('So, the correct answer is ' + correct_answer_backticked)
            
            // setCorrectAnswer wraps the answer in backticks, so let's remove them.
            correct_answer = correct_answer_backticked.replace(/`/gi, '')
   		}

		setCorrectAnswer(correct_answer);
    }
    
    function generateWrongAnswers() {
        if (get_random() > 0)
            addWrongChoice('`No solution`')
        
        var numerator = right_c[0];
		var denominator = left_x[0];
		while (getNumPossibleAnswers() < 6)
		{
    			var n_shift = get_random();
    			var d_shift = get_random();

    			while (d_shift+denominator == 0)
    				d_shift = get_random();

    			wrong_numerator = Math.abs(numerator + n_shift)
    			wrong_denominator = Math.abs(denominator + d_shift)
    			wrong_answer = format_fraction(wrong_numerator, wrong_denominator)
    			
    			if (wrong_answer == 0)
    			    addWrongChoice('x=' + wrong_answer);
    			else
    			    addWrongChoice('x= - ' + wrong_answer + ' or x=' + wrong_answer);               
		}
    }
}

