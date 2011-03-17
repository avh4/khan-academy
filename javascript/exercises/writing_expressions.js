// Translating Word Problems Into Equations
// Author: Marcia Lee
// Date: 2011-03-16
//
// Problem layout:
// (multiple choice, and none of the above?)
// -- the sum of
// -- the difference
// -- a is 5 more than b
// -- a is 5 more than the product of 3 and b
// -- a is 
// -- quotient / dividend / divisor
// -- add meaning, like age, dollars, speed.
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
    
    this.toColorCoded = function() {
        return "<span style='color: blue'>" + clauses[0]+ "</span>" + "<span style='color: orange'>" + clauses[1] + "</span>";
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
        setCorrectAnswer(expression.toString());
    }
    
    function showHints() {
        write_text("Let's break this phrase into smaller parts.");
        open_left_padding(30);
        write_text(expression.toColorCoded());
        write_text("This translates to: `" + expression.getConstant() + "` and `" +  expression.getCoefficient() + expression.getVariable()) + "`";
        write_text("Or: `" + expression.getConstant() + " + " + expression.getCoefficient() + expression.getVariable() + "`");
        write_text("Reordering the terms gives: `" + expression.toString()) + "`";
        close_left_padding();
    }
    
    
    function generateWrongAnswers() {
        var wrong = new SimpleExpression();
        wrong.setCoefficient(expression.getCoefficient() * -1);
        addWrongChoice(wrong.toString());
        
        wrong.setConstant(expression.getConstant() * -1);
        addWrongChoice(wrong.toString());
        
        wrong.setCoefficient(expression.getConstant());
        wrong.setConstant(expression.getCoefficient());
        if (!expression.equals(wrong)) 
            addWrongChoice(wrong.toString());

        while (getNumPossibleAnswers() < 4) {
            wrong = new SimpleExpression();
            addWrongChoice(wrong.toString());
        }
    }
    

    
        

}

