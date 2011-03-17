// Writing Expressions 1
// Author: Marcia Lee
// Date: 2011-03-16
//
// Problem layout:
// Select the expression that represents the following phrase:
//  b more/less than the product of a and x
//  answer == ax + b or none of the above
// Constraints: a and b are ints in [-10, 10] except 0
// 
// 


function SimpleExpression() {
    var coeff = get_random();
    var variable = "x";
    var constant = get_random();
    var numbers = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"];
    var clauses = {};
    var is_easier = get_random() > 5;
    
    this.toString = function() {
        return "" + format_first_coefficient(coeff) + variable + format_constant(constant);
    }
    
    this.toEnglish = function() {
        var result = "";
        var clause = "";
        
        if (!is_easier) {
            clause += numbers[Math.abs(constant)]
            if (constant > 0)
                clause += " more than "
            else if (constant < 0)
                clause += " less than "
            clauses.outer = clause;
            result += clause;
        }
        
        clause = " the product of "
        if (coeff < 0)
            clause += " negative ";
        clause += numbers[Math.abs(coeff)] + " and ";
        clause += " " + variable;
        clauses.inner = clause;
        result += clause;
            
        if (is_easier) {
            clause = "";
            if (constant > 0)
                clause += " plus "
            else
                clause += " minus "
            clause +=  numbers[Math.abs(constant)]
            clauses.outer = clause;
            result += clause;
        }
        
        return result;
    }
    
    this.showHints = function() {
        write_step("Let's break this phrase into smaller parts.");
        
        open_left_padding(30);
        var outer_clause = format_string_with_color(clauses.outer, "blue");
        var inner_clause = format_string_with_color(clauses.inner, "orange");
        if (is_easier)
            write_step(inner_clause + outer_clause);
        else
            write_step(outer_clause + inner_clause);

        write_step("What is " + inner_clause + "?");
        var inner_expression = format_math_with_color(format_first_coefficient(coeff) + variable, "orange");
        write_step("`" + coeff + " * " + variable + " = ` "+ inner_expression);
        
        if (is_easier)
            write_step("What is " + inner_expression + " " + outer_clause + "?");
        else
            write_step("What is " + outer_clause + " " + inner_expression + "?");
        
        var outer_expression = format_math_with_color(format_constant(constant), "blue");
        
        write_step(inner_expression + outer_expression);


        close_left_padding();
        
        write_step("So, " + this.toEnglish() + " can be written as "  + "`" + this.toString() + "`");
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

function WritingExpressionsExercise() {
    var expression;
    
    showProblem();
    showHints();
    generateWrongAnswers();
    
    function showProblem() {
        expression = new SimpleExpression();
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
        
        var wrong = new SimpleExpression();
        wrong.setCoefficient(expression.getCoefficient() * -1);
        wrong.setConstant(expression.getConstant());
        addWrongChoice(wrong.toString());
        
        wrong.setConstant(expression.getConstant() * -1);
        addWrongChoice(wrong.toString());
        
        wrong.setCoefficient(expression.getConstant());
        wrong.setConstant(expression.getCoefficient());
        if (!expression.equals(wrong)) 
            addWrongChoice(wrong.toString());
        
        wrong.setCoefficient(expression.getConstant() * -1);
        wrong.setConstant(expression.getCoefficient() * -1);
        if (!expression.equals(wrong))
            addWrongChoice(wrong.toString());

        while (getNumPossibleAnswers() < 4) {
            wrong = new SimpleExpression();
            addWrongChoice(wrong.toString());
        }
    }
}

