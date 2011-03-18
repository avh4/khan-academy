// Evaluating Expressions 1
// Author: Marcia Lee
// Date: 2011-03-17
//
// Problem layout:
//  Evaluate an expression of the form ax + b for some random x
//

// Expression of the form ax + b
function Expression() {
    var coeff = get_random();
    var variable = "x";
    var input_value = get_random();
    var constant = get_random();
    
    this.toString = function() {
        return "" + format_first_coefficient(coeff) + variable + format_constant(constant);
    }
    
    this.showHints = function() {
        var input_value_text = format_math_with_color(input_value, "orange");
        write_step("Plug in " + input_value_text + " for `" + variable + "`.");
        
        open_left_padding(30);
        write_step("`(" + coeff + ") * (`" + input_value_text + "`)" + format_constant(constant)) + "`";
        
        var product_text = format_math_with_color("(" +  coeff + ") * (" + input_value + ")", "orange");
        write_step("`=` " + product_text + "`" + format_constant(constant) + "`");
        
        product_text = format_math_with_color(coeff * input_value, "orange");
        write_step("`=` " + product_text + "`" + format_constant(constant) + "`");
        
        var answer_text = format_math_with_color(this.getValue(), "orange");
        write_step("`=` " + answer_text);
        
        close_left_padding();

        write_step("So, the answer is `" + this.getValue() + "`.");
    }
    
    this.getValue = function() {
        return coeff * input_value + constant;
    }
    this.getCoefficient = function() {
        return coeff;
    }
    
    this.getConstant = function() {
        return constant;
    }
    
    this.getVariable = function() {
        return variable;
    }
    
    this.getInputValue = function() {
        return input_value;
    }
    
    this.setCoefficient = function(new_coeff) {
        coeff = new_coeff;
    }
    
    this.setConstant = function(new_constant) {
        constant = new_constant;
    }
    
    this.equals = function (other_expression) {
        return coeff == other_expression.getCoefficient() && constant == other_expression.getConstant();
    }
}

function EvaluatingExpressionsExercise() {
    var expression;
    showProblem();
    showHints();
    setCorrectAnswer(10);
    
    function showProblem() {
        expression = new Expression();
        write_text("Evaluate the following expression when `x = " + expression.getInputValue() + "`.");
        
        open_left_padding(30);
        write_text("`" + expression.toString() + "`");
        close_left_padding(); 
    }
    
    function showHints() {
        expression.showHints();
    }
}
