// Translating Word Problems Into Equations
// Author: Marcia Lee
// Date: 2011-03-16
//
// Problem layout:
// Select the expression that represents the following phrase:
//  b more/less than the product of a and x
//  answer == ax + b or none of the above
// Constraints: a and b are ints in (-10, 10) except 0
// 
// 


function SimpleExpression() {
    var coeff = get_random();
    var variable = "x";
    var constant = get_random();
    var numbers = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"];
    var clauses = [];
    
    this.toString = function() {
        return "" + format_first_coefficient(coeff) + variable + format_constant(constant);
    }
    
    this.toEnglish = function() {
        var result = "";
        var clause = "";
        if (constant > 0)
            clause += " " + numbers[constant] + " more than "
        else if (constant < 0) {            
            clause += " " + numbers[Math.abs(constant)] + " less than "
        }

        clauses.push(clause);
        result += clause;
        clause = "";
        
        clause += " the product of "
        if (coeff < 0)
            clause += " negative ";
        clause += numbers[Math.abs(coeff)] + " and ";
        clause += " " + variable;
        
        clauses.push(clause);
        result += clause;
        
        return result;
    }
    
    this.showHints = function() {
        write_step("Let's break this phrase into smaller parts.");
        
        open_left_padding(30);
        var blue_clause = format_string_with_color(clauses[0], "blue");
        var orange_clause = format_string_with_color(clauses[1], "orange");
        write_step(blue_clause + orange_clause);

        write_step("What is " + orange_clause + "?");
        var orange_math = format_math_with_color(format_first_coefficient(coeff) + variable, "orange");
        write_step("`" + coeff + " * " + variable + " = ` "+ orange_math);
        
        write_step("What is " + blue_clause + " " + orange_math + "?");
        var blue_math = format_math_with_color(format_constant(constant), "blue");
        write_step(orange_math + blue_math);
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
            setCorrectAnswer("`None of the above`");
    }
    
    function showHints() {
        expression.showHints();
    }
    
    function generateWrongAnswers() {
        // If None of the above is the correct answer, then the following has no effect.
        addWrongChoice("`None of the above`");
        
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

