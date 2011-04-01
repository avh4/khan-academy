// Writing Expressions 1
// Author: Marcia Lee
// Date: 2011-03-16
//
// Problem layout:
// Select the expression that represents the following phrase:
    
    // b plus the product of a and x
    // b plus the quantity a times x
    
    // the sum of b and the product of a and x
    // the sum of b and the quantity a times x

    // take the product of a and x, and then add/subtract b
    // take the quantity a times x, and then add/subtract b
    
//  answer == ax + b or none of the above
// Constraints: a and b are ints in [-10, 10] except 0
// 
// 

function WritingExpressionsExercise() {
    var expression = new Expression();
    var orig_answer;
    
    showProblem();
    showHints();
    generateWrongAnswers();
    
    function showProblem() {
        write_text("Select the expression that matches the following phrase: ");
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
        
        write_step("So, the original phrase can be written as "  + "`" + expression.toString() + "`");
    }
    
    function generateWrongAnswers() {
        addWrongChoiceIfNotOrig("`None of these`");
        
        var wrong = new Expression();
        wrong.setCoefficient(expression.getCoefficient() * -1);
        wrong.setConstant(expression.getConstant());
        addWrongChoiceIfNotOrig(wrong.toString());
        
        wrong.setConstant(expression.getConstant() * -1);
        addWrongChoiceIfNotOrig(wrong.toString());
        
        wrong.setCoefficient(expression.getConstant());
        wrong.setConstant(expression.getCoefficient());
        addWrongChoiceIfNotOrig(wrong.toString());
        
        wrong.setCoefficient(expression.getConstant() * -1);
        wrong.setConstant(expression.getCoefficient() * -1);
        addWrongChoiceIfNotOrig(wrong.toString());

        while (getNumPossibleAnswers() < 4) {
            wrong = new Expression();
            addWrongChoiceIfNotOrig(wrong.toString());
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
