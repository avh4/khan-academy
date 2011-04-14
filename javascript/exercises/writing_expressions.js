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
        setCorrectAnswer(orig_answer);
    }
    
    function showHints() {
        write_step("Let's break this problem into smaller and easier pieces.");
        
        open_left_padding(30);
        expression.showHints();
        close_left_padding();
        
        write_step("So, the original phrase can be written as "  + "`" + expression.toString() + "`");
    }
    
    function generateWrongAnswers() {
        var wrong = new Expression();
        wrong.setCoefficient(expression.getCoefficient() * -1);
        wrong.setConstant(expression.getConstant());
        addWrongChoice(wrong.toString());
        
        wrong.setConstant(expression.getConstant() * -1);
        addWrongChoice(wrong.toString());
        
        wrong.setCoefficient(expression.getConstant());
        wrong.setConstant(expression.getCoefficient());
        addWrongChoice(wrong.toString());
        
        wrong.setCoefficient(expression.getConstant() * -1);
        wrong.setConstant(expression.getCoefficient() * -1);
        addWrongChoice(wrong.toString());

        while (getNumPossibleAnswers() < 4) {
            wrong = new Expression();
            addWrongChoice(wrong.toString());
        }
    }
}
