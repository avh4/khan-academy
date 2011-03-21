// Writing Expressions 2
// Author: Marcia Lee
// Date: 2011-03-17
//
// Problem layout:
// a times the sum of x and b
// a times the difference of x and b
// 
//

// Expression of the form a * (x + b)
function Expression() {
    var factor = get_random();
    var variable = "x";
    var constant = get_random();
    var numbers = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"];
    var clauses = {};
    var is_easier = get_random() > 5;
    
    this.toString = function() {
        return factor + " * ( " + variable + format_constant(constant) +" ) ";
    }
    
    this.toEnglish = function() {
        var result = "";
        var clause = "";
        
        if (is_easier)
            clause = factor + " times ";
        else
            clause = "the product of " + factor + " and ";

        clauses.outer = clause;
        result += clause;
        
        clause = "";
        if (constant > 0)
            clause += " the sum of ";
        else
            clause += " the difference of ";
            
        clause += variable + " and " + Math.abs(constant);
 
        clauses.inner = clause;
        result += clause;

        return result;
    }
    
    this.showHints = function() {
        write_step("Let's break this phrase into smaller parts.");
        
        open_left_padding(30);
        var outer_clause = format_string_with_color(clauses.outer, "blue");
        var inner_clause = format_string_with_color(clauses.inner, "orange");
        write_step(outer_clause + inner_clause);

        write_step("What is " + inner_clause + "?");
        var inner_expression = format_math_with_color(variable + format_constant(constant), "orange");
        write_step(inner_expression);

        inner_expression = format_math_with_color("(" + variable + format_constant(constant) + ")", "orange");
        write_step("What is " + outer_clause + " " + inner_expression + "?");
        
        var outer_expression = format_math_with_color(factor + " * ", "blue");
        write_step(outer_expression + inner_expression);

        close_left_padding();
        
        write_step("So, " + this.toEnglish() + " can be written as "  + "`" + this.toString() + "`");
    }
    
    this.getFactor = function() {
        return factor;
    }
    
    this.getConstant = function() {
        return constant;
    }
    
    this.getVariable = function() {
        return variable;
    }
    
    this.setFactor = function(new_factor) {
        factor = new_factor;
    }
    
    this.setConstant = function(new_constant) {
        constant = new_constant;
    }
    
    this.equals = function (other_expression) {
        return factor == other_expression.getFactor() && constant == other_expression.getConstant();
    }
}

function WritingNestedExpressionsExercise() {
    var expression;
    
    showProblem();
    showHints();
    generateWrongAnswers();
    
    function showProblem() {
        expression = new Expression();
        write_text("Select the expression that represents the following phrase: ");
        open_left_padding(30);
        write_text(expression.toEnglish());
        close_left_padding();
        
        var answer = expression.toString();
        if (get_random() > -5) 
            setCorrectAnswer(expression.toString());
        else
            setCorrectAnswer("`None of these`");
    }
    
    function showHints() {
        expression.showHints();
    }
    
    function generateWrongAnswers() {
        // If None of the above is the correct answer, then the following has no effect.
        addWrongChoice("`None of these`");
        
        var wrong = new Expression();
        wrong.setFactor(expression.getFactor() * -1);
        wrong.setConstant(expression.getConstant());
        addWrongChoice(wrong.toString());
        
        wrong.setConstant(expression.getConstant() * -1);
        addWrongChoice(wrong.toString());
        
        wrong.setFactor(expression.getConstant());
        wrong.setConstant(expression.getFactor());
        if (!expression.equals(wrong)) 
            addWrongChoice(wrong.toString());
        
        wrong.setFactor(expression.getConstant() * -1);
        wrong.setConstant(expression.getFactor() * -1);
        if (!expression.equals(wrong))
            addWrongChoice(wrong.toString());

        while (getNumPossibleAnswers() < 4) {
            wrong = new Expression();
            addWrongChoice(wrong.toString());
        }
    }
}
