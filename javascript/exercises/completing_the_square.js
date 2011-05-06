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
        var temp;
        if (x2 < x1) {
            temp = x1;
            x1 = x2;
            x2 = temp;
        }
            
        setCorrectAnswer(formatAnswer(x1, x2));
        
        if (getRandomIntRange(1, 10) <= 4) {
            leadingCoefficient = getRandomIntRange(1, 6);
            if (getRandomIntRange(0, 1) || leadingCoefficient == 1) { // make it negative half the time
                leadingCoefficient *= -1;
            }
        }
        
        while (Exercise.getNumPossibleAnswers() < 4) {
            var fake_c = nonZeroRandomInt(-12, 12);
            var f1 = -a - fake_c;
            var f2 = -a + fake_c;
            // smaller number first, again
            if (f2 < f1) {
                temp = f1;
                f1 = f2;
                f2 = temp;
            }
            addWrongChoice(formatAnswer(f1, f2));
        }
    }
    
    function formatAnswer(first, second) {
        return "x = " + first + " and " + " x = " + second;
    }
    
    function showProblem() {
        write_text("Solve the following quadratic equation by completing the square:");
        write_text(equation_string(format_first_coefficient(leadingCoefficient) + "x^2 " + format_coefficient(2 * a * leadingCoefficient) + "x " + format_constant(n * leadingCoefficient) + " = 0"));
    }
    
    function generateHints() {
        open_left_padding(30);
        
        write_step("Remember, completing the square is about getting the equation to this form:" + equation_string("(x + a)^2 = x^2 + 2ax + a^2"));
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
            write_step(phrase + "both sides, resulting in this equation:" + equation_string("x^2 " + format_coefficient(2 * a) + "x = " + -n));
        write_step("In the problem above, `2ax = " + (2 * a) + "x`. Therefore, `a = (" + (2 * a) + "x)/(2x) = " + a + "`.");
        write_step("Add `a^2` to both sides, giving:" + equation_string("x^2 " + format_coefficient(2 * a) + "x + " + a * a + " = " + ((a * a) - n)));
        write_step("Rewrite the problem as:" + equation_string("(x " + format_constant(a) + ")^2 = " + ((a * a) - n)) + "Get the square root of both sides, and solve for x.");
        write_step(equation_string("x " + format_constant(a) + " = +-" + Math.abs(c)));
        write_step(equation_string("x = " + x1 + " and x = " + x2))
        
        close_left_padding();
    }

    generateProblem();
    showProblem();
    generateHints();
}
