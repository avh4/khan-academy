// Writing Expressions 2
// Author: Marcia Lee
// Date: 2011-03-17
//
// Problem layout:
//  nest expressions
//  eg: -1 plus the product of -5 and the sum of -5 and the product of 7 and x ==> −5(7x−5)−1
// 
//

function WritingNestedExpressionsExercise() {
    var inner_expression = new Expression();
    var expression = new Expression();
        
    expression.setInner(inner_expression);
    
    showProblem();
    showHints();
    generateWrongAnswers();
    
    function showProblem() {
        write_text("First consider the expression for: ");
        open_left_padding(30);
        write_text(inner_expression.toEnglish());
        close_left_padding();
        
        write_text("Now select the answer that matches the following: ");
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
        write_step("Let's break this problem into smaller and easier pieces.");

        open_left_padding(30);
        expression.showHints();
        close_left_padding();
        
        write_step("So, the entire expression can be written as "  + "`" + expression.toString() + "`");
    }
    
    function generateWrongAnswers() {
        // If None of the these is the correct answer, then the following has no effect.
        addWrongChoice("`None of these`");
        
        var coeff = expression.getCoefficient();
        var constant = expression.getConstant();
        
        var inner_coeff = inner_expression.getCoefficient();
        var inner_constant = inner_expression.getConstant();
        
        expression.setCoefficient(coeff * -1);
        addWrongChoice(expression.toString());
        
        expression.setConstant(constant * -1);
        inner_expression.setCoefficient(inner_constant);
        inner_expression.setConstant(inner_coeff);
        addWrongChoice(expression.toString());
        
        expression.setCoefficient(constant);
        expression.setConstant(coeff);
        addWrongChoice(expression.toString());
        
        inner_expression.setCoefficient(inner_coeff);
        inner_expression.setConstant(inner_constant * -1);
        addWrongChoice(expression.toString())

        while (getNumPossibleAnswers() < 4) {
            expression.setConstant(get_random());
            addWrongChoice(expression.toString());
        }
    }
}
