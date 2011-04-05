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
    var orig_answer;
        
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
        
        orig_answer = expression.toString();
        if (get_random() > -5) 
            setCorrectAnswer(orig_answer);
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
        addWrongChoiceIfNotOrig("`None of these`");
        
        var coeff = expression.getCoefficient();
        var constant = expression.getConstant();
        
        var inner_coeff = inner_expression.getCoefficient();
        var inner_constant = inner_expression.getConstant();
        
        expression.setCoefficient(coeff * -1);
        addWrongChoiceIfNotOrig(expression.toString());
        
        expression.setConstant(constant * -1);
        inner_expression.setCoefficient(inner_constant);
        inner_expression.setConstant(inner_coeff);
        addWrongChoiceIfNotOrig(expression.toString());
        
        expression.setCoefficient(constant);
        expression.setConstant(coeff);
        addWrongChoiceIfNotOrig(expression.toString());
        
        inner_expression.setCoefficient(inner_coeff);
        inner_expression.setConstant(inner_constant * -1);
        addWrongChoiceIfNotOrig(expression.toString())

        while (getNumPossibleAnswers() < 4) {
            expression.setConstant(get_random());
            addWrongChoiceIfNotOrig(expression.toString());
        }
    }
    
    // When the correct answer is rigged to "None of the these", 
    // we don't want a wrong answer to be correct.
    // Eventually, refactor this into exerciseutil 
    // so that all exercises with a "None of these" option will benefit.
    function addWrongChoiceIfNotOrig(wrong_str) {
        if (wrong_str != orig_answer)
            addWrongChoice(wrong_str)
    }
}
