// Radical Equations
// Author: Marcia Lee
// Date: 2011-03-01
//
// Problem layout:
// Solve an equation of the form:  ax + b = cx + d
//  Because this problem uses get_random(), 
//  the variables are non-zero integers between -10 and 10.
//  a cannot equal c, but b can equal d.
//
// absolute_value_equations.js and radical_equations.js extend this
// by passing "|x|" and "sqrt(x)" in to init, respectively.
//
// In theory, linear_equations_1 could be refactored to use this.
//

function LinearEquations() {
    var left_x = [get_random()]; 
    var right_x = [get_random()];
    var left_c = [get_random()];
    var right_c = [get_random()];
    var var_str = ""

    this.init = function(s) {
        while (right_x[0] == left_x[0])
            right_x[0] = get_random();

        var_str = ' ' + s + ' ';
        showProblem();    
        generateHints();
     }

    function showProblem() {
        write_text("Solve for `x`:");

        var lhs = format_expression(left_x, var_str, noSelColor, true) + format_expression(left_c, '', noSelColor, false)
        var rhs = format_expression(right_x, var_str, noSelColor, true) + format_expression(right_c, '', noSelColor, false)

        table_step_header('', lhs, rhs);
     }

     function generateHints() {
        addXTerm();                 // Add -c|x| to both sides
        addConstant();              // Add -b
        multiplyCoefficient();      // Multiply by 1/a
     }

     function addXTerm() {
        var term = format_first_coefficient(Math.abs(right_x[0])) + var_str;
        var term_html = format_string_with_color(term, selColor);

        var step = generateHint(right_x[0], term_html);
        var lhs = step.lhs_term + format_expression(left_x, var_str, noSelColor, false) + format_expression(left_c, '', noSelColor, false);
        var rhs = format_expression(right_x, var_str, noSelColor, true) + format_expression(right_c, '', noSelColor, false) + step.rhs_term;
        write_table_step(step.explanation, lhs, rhs);

        var explanation = format_expression([-1 * right_x[0], left_x[0]], var_str, selColor, true)
        explanation += format_string_with_color('=', selColor) + format_expression([left_x[0]-right_x[0]], var_str, selColor, true)

        explanation += '; ';
        explanation += format_expression([right_x[0],-1*right_x[0]], var_str, selColor, true) + format_string_with_color('=0', selColor);

        left_x = [left_x[0]-right_x[0]];
        right_x = [];

        lhs = format_expression(left_x, var_str, selColor, true) + format_expression(left_c, '', noSelColor, false)
        rhs =  format_expression(right_c, '', noSelColor, true)

        write_table_step(explanation, lhs, rhs);
     }

     function addConstant() {
        var term = Math.abs(left_c[0]);
        var term_html = format_string_with_color(term, selColor);

        var step = generateHint(left_c[0], term_html);

        var lhs = step.lhs_term + format_expression(left_x, var_str, noSelColor, false)
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

        lhs = format_expression(left_x, var_str, noSelColor, true)
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

 		var lhs = term_html + '`*`'+format_expression(left_x, var_str, noSelColor, true);
 		var rhs = format_expression(right_c, '', noSelColor, true)+'`*`' + term_html;
 		write_table_step(explanation, lhs, rhs);

 		explanation = "Simplify.";
 		write_table_step(explanation, var_str, format_fraction(right_c[0], left_x[0]));

 		table_step_footer();
     }
     
     this.getLeftCoeff = function() {
         if (left_x.length)
             return left_x[0];
         return 0;
     }

     this.getRightCoeff = function() {
         if (right_x.length)
             return right_x[0];
         return 0;
     }

     this.getLeftConstant = function() {
         if (left_c.length)
             return left_c[0];
         return 0;
     }

     this.getRightConstant = function() {
         if (right_c.length)
             return right_c[0];
         return 0;
     }
}
