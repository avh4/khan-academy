// Logarithms 2
// Author: Jens Axel Søgaard
// Date: 2012-03-16
//
// Problem spec:
//   
//
// Related Videos:
// Introduction to logarithm properties, part 1
//    http://www.youtube.com/watch?v=PupNgv49_WY
// Introduction to logarithm properties, part 2
//   http://www.youtube.com/watch?v=TMmxKZaCqe0

// Problem layout:
//   You get expressions of the types:
//       1) log(a)+log(b), 
//       2) log(a)-log(b), 
//       3) n*log(a)
//   and must rewrite this to the form  log(c). 

function Logarithms2Exercise() {
    var a = 1;
    var b = 1;
    var type = 1;
    var correct = 1;

    this.init = function() {
	generateProblem();
	generateWrongChoices();
	showProblem();
	generateHints();
    }

    function generateProblem() {
	type = getRandomIntRange(1,3);
	b = getRandomIntRange(2,5);
	a = getRandomIntRange(2,5);
	if (type == 2) // log(a)-log(b)
	    a = a*b;   // make sure b divides a
	switch (type) {
  	case 1: // log(a)+log(b)
	    correct = a*b;
	    break;
   	case 2: // log(a)-log(b)
	    correct = a/b;
	    break;
 	case 3: // b*log(a)
	    correct = Math.pow(a,b);
	    break;
	}
	setCorrectAnswer( formatAnswer(correct) );
   }

    function generateWrongChoices() {
	addWrongChoiceIfIncorrect( a+b );
	addWrongChoiceIfIncorrect( a-b );
	addWrongChoiceIfIncorrect( a*b );
	addWrongChoiceIfIncorrect( a/b );
	addWrongChoiceIfIncorrect( Math.pow(a,b) );
    }
    
    function addWrongChoiceIfIncorrect(wrong, correct) {
	if (!(wrong==correct))
	    addWrongChoice( formatAnswer(wrong) );
    }

    function formatAnswer(a) {
	if (a<=0)
	    a = -a+1; // make sure a is positive
	return  "`log(" + a + ")`";
    }

    function showProblem() {
	switch (type) { 
	case 1: // log(a)+log(b)
	    write_text("`log(" +a+ ") + log(" +b+ ") = ?`");
	    break;
	case 2: // log(a)-log(b)
	    write_text("`log(" +a+ ") - log(" +b+ ") = ?`");
	    break;
	case 3: // b*log(a)
	    write_text("`" + b + "\\cdot log(" +a+ ") = ?`");
	    break;
	}
    }

    function generateHints() {
	var pre = "<span class='hint_orange'>";
	var post = "</span>";
	// First hint
	open_left_padding(30);
	switch (type) {
	case 1: 
	    write_step(pre+"Use the rule:  `log(a)+log(b)=log(a\\cdot b)`"+post);
	    break;
	case 2: 
	    write_step(pre+"Use the rule:  `log(a)-log(b)=log(\\frac{a}{b})`"+post);
	    break;
	case 3: 
	    write_step(pre+"Use the rule:  `n\\cdot log(a)=log(a^n)`"+post);
	    break;
	}
	close_left_padding();
	// Second hint
	open_left_padding(30);
	switch (type) {
	case 1: 
	    write_step(pre+"Use the rule:  `log("+a+")+log("+b+")=log("+a+"\\cdot "+b+")`"+post);
	    break;
	case 2: 
	    write_step(pre+"Use the rule:  `log("+a+")-log("+b+")=log(\\frac{"+a+"}{"+ b+"})`"+post);
	    break;
	case 3: 
	    write_step(pre+"Use the rule:  `"+b+"\\cdot log("+a+")=log("+a+"^"+b+")`"+post);
	    break;
	}
	close_left_padding();
    }
}