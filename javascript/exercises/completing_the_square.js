/*
    Completing the Square
    Author: Dave Sescleifer
    Date: 2011-04-16
    
    Problem layout:
    Solve a quadratic equation by completing the square.
    
    A and C are random numbers between -12 and 12.
    A is the same A as seen in (x + a)^2 = x^2 + 2ax + a^2.
    C is the number in x = -a +- c.
*/
function CompletingTheSquareExercise() {
    var a;
    var c;
    var n; // N is the constant in the original problem. It is a^2 - c^2, so that the answer turns out nicely.
    var x1; // these are global for the hints
    var x2;
    var leadingCoefficient = 1;

    function generateProblem() {
        a = nonZeroRandomInt(-12, 12);
        c = nonZeroRandomInt(-12, 12);
        n = a * a - c * c;
        x1 = -a - c;
        x2 = -a + c;
        
        // present smaller number first
        x1 = Math.min(x1, x2);
        x2 = Math.max(x1, x2);
        
        if (getRandomIntRange(1, 10) <= 4) {
            leadingCoefficient = getRandomIntRange(1, 6);
            if (getRandomIntRange(0, 1) || leadingCoefficient == 1) { // make it negative half the time
                leadingCoefficient *= -1;
            }
        }
    }
    
    function showProblem() {
        write_text("Complete the square:");
        write_text(equation_string(format_first_coefficient(leadingCoefficient) + "x^2 " + format_coefficient(2 * a * leadingCoefficient) + "x " + format_constant(n * leadingCoefficient) + " = 0"));
        write_text("To answer this question, provide the values of `a` and `b` (not of `x`).");
        write_text(equation_string("(x + a)^2 = b^2"));
    }
    
    function generateHints() {
        open_left_padding(30);

        write_step("Notice the following: " + equation_string("(x + a)^2 = x^2 + 2ax + a^2"));
        if (leadingCoefficient != 1) {
            write_step("Divide the entire equation by `" + leadingCoefficient + "` to get " + equation_string("x^2 " + format_coefficient(2 * a) + "x " + format_constant(n) + " = 0"));
        }
        var phrase;
        if (n >= 0) {
            phrase = "Subtract `" + n + "` from ";
        } else {
            phrase = "Add `" + -n + "` to ";
        }
        if (n != 0)
            write_step(phrase + "both sides of the original equation:" + equation_string("x^2 " + format_coefficient(2 * a) + "x = " + -n));
        write_step("We see that `2ax ` corresponds with `" + (2 * a) + "x`. Therefore, `2ax = " + (2 * a) + "x `" 
                    + " and  " + "`a = (" + (2 * a) + "x)/(2x) = " + a + "`.");
        write_step("Add `a^2` or `" + (a * a) + "` to both sides:" + equation_string("x^2 " + format_coefficient(2 * a) + "x + " + a * a + " = " + ((a * a) - n)));
        write_step("This can be rewritten as:" + equation_string("(x " + format_constant(a) + ")^2 = " + ((a * a) - n)));
        write_step("So, `a = " + a + "` and `b = " + c + "`.");
        write_step("To solve for x, take the square root of both sides.");
        write_step(equation_string("x " + format_constant(a) + " = +-" + Math.abs(c)));
        write_step(equation_string("x = " + x1 + " and x = " + x2));
        
        close_left_padding();
    }

    generateProblem();
    showProblem();
    generateHints();
    
    this.checkAnswer = function() {
        var result_a = isInputCorrect($("#answer_a").val(), a, 0);
        var result_b = isInputCorrect($("#answer_b").val(), c, 0);
        
        if (result_a == Answer.INVALID || result_b == Answer.INVALID) {
            $("#answer_a").focus();
            return Answer.INVALID;            
        }

        if (result_a == Answer.CORRECT && result_b == Answer.CORRECT)
            return Answer.CORRECT;
            
        $("#answer_a").focus();
        return Answer.INCORRECT;
    }
}
