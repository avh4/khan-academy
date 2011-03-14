function updatePreview()
{
    var str = '`'+$("#answer").val()+'`';

    var outnode = $("#outputNode").get(0);
    $("#outputNode").html("");
    outnode.appendChild(document.createTextNode(str));
    
    AMprocessNode(outnode);
    MathJax.Hub.Queue(["Typeset",MathJax.Hub,outnode]);
}

function checkExpressionAnswer()
{
    // Check if the expression entered matches our desired answer expression
    // The current strategy is to evaluate the user's answer vs. our answer
    // at several randomly defined points. If they align, the answer is right.

    var usersAnswer = $("#answer").val();

    // Use ASCIIsvg-wrapper's tools to convert the right expression
    // into the JS function f.
    // FIXME no support for non-x variables
    eval("f = function(x){ with(Math) return "+mathjs(correctAnswer)+" }");
    // User's expression -> g(x)
    try {
	eval("g = function(x){ with(Math) return "+mathjs(usersAnswer)+" }");
    } catch (ex) {
	alert("Your answer doesn't make sense as a math expression.");
	return;
    }
    var isCorrect = true;
    var randX;

    // Test (arbitrary) 10 points between f and g
    // FIXME may break on sqrt() and other functions given negative x
    for (var i = 0; i < 10; i++) {
	randX = getRandomIntRange(-1000, 1000) / 10; // range + decimal is arbitrary
	if ((!isNaN(f(randX)) && isNaN(g(randX))) ||
	    (Math.abs(f(randX) - g(randX)) > 0.01)) {
	    isCorrect = false;
	}
    }

    handleCorrectness(isCorrect);
}
