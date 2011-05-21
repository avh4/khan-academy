/* 
Fractional Exponents 1 Problems
Author: Sophia Westwood and Grant Mathews
Date: 2011-04-19

Problem spec: 
    Basic fractional exponents. Numerator is always 1.
    Denominator is between 2 and 5. Base is between 0 and 200. 
    Fraction is always < 1. 
*/  


function FractionalExponents1Exercise() {
    var problem = {};
    var wrongVals = [];
    var NUMERATOR = 1; // Always 1 for Fractional Exponents 1
    var MAX_DENOMINATOR = 5;
    var MAX_BASE = 200;


    var LARGEST_ALLOWED = Math.pow(10, 5);
    var MIN_NUM_CHOICES = 4; // TODO: put this constant in a centralized javascript file


    generateProblem();
    showProblem();
    generateHints();

/* Generates a problem of the form base ^ (1 / denominator). Sets up instance var 'problem' and generates wrong choices. */
    function generateProblem() {
       problem.numerator = NUMERATOR;
       problem.denominator = getRandomIntRange(NUMERATOR + 1, MAX_DENOMINATOR); // denominator can't be zero, numerator/denominator < 1
       problem.base = getRandomInt(MAX_BASE); // base will sometimes be 0
       var correctAnsStr = 'root ' + problem.denominator + '` ' + problem.base + '`';
       var correctAnsVal = Math.pow(problem.base, (problem.numerator / problem.denominator));
       setCorrectAnswer(getNicestEvaluation(correctAnsVal, correctAnsStr));
       addWrongChoices();
    }

    /* 
      Adds wrong answer choices, calling tryAddWrongChoice for safety.
      Assumption: Denominator is never 0. */
    function addWrongChoices() {
      if (problem.base != 0) {
        tryAddWrongChoice(Math.pow(problem.base, 1/(problem.denominator)), 'root ' + problem.denominator + '` ' + problem.base + '`');
        tryAddWrongChoice(Math.pow(problem.denominator, 1/problem.base), 'root ' + problem.base + '` ' + problem.denominator + '`');
        tryAddWrongChoice(problem.denominator / problem.base, format_fraction(problem.denominator, problem.base));
        tryAddWrongChoice(problem.denominator/(problem.base*problem.numerator) , format_fraction(problem.denominator, problem.base * problem.numerator)); // numerator is always 1
    }
      tryAddWrongChoice(problem.numerator/problem.denominator, format_fraction(problem.numerator, problem.denominator));
      tryAddWrongChoice(problem.denominator, problem.denominator);
      tryAddWrongChoice(problem.denominator*problem.base, problem.denominator * problem.base);
      tryAddWrongChoice(problem.base / problem.denominator, format_fraction(problem.base, problem.denominator));
      tryAddWrongChoice(Math.pow(problem.denominator * problem.base, 1/problem.denominator), 'root ' + problem.denominator + '` ' + problem.denominator * problem.base + '` ')
      tryAddWrongChoice((problem.base*problem.numerator) / problem.denominator, format_fraction(problem.base * problem.numerator, problem.denominator)); // numerator is always 1
      if (wrongVals.length < MIN_NUM_CHOICES) { // ensures that there are always at least 5 wrong answers. Probably happens when answer value is 1 or 0
        tryAddWrongChoice(0, "0");
        tryAddWrongChoice(1.0/2, format_fraction(1, 2));
        tryAddWrongChoice(1.0/3, format_fraction(1, 3));
        tryAddWrongChoice(1, "1");
        tryAddWrongChoice(4, "4");
      }  
}


  /* Returns a string of the "prettiest" reduced version of proposedValStr, given that proposedVal is the evaluation of proposedValStr. 
    Ex: transforms "1^(1/4)" into "1" and transforms "4^(1/2)"" into "2" */
  function getNicestEvaluation(proposedVal, proposedValStr){
    var close = Math.round(proposedVal); // nearest integer.
    if (doublesEquals(Math.abs(proposedVal-close), 0))
      return close + "";
    return proposedValStr;
  }

    /* Only adds the wrong answer choice after checking that it does not evaluate to the correct answer, or to any previously added wrong values.
     Precondition: answerStr evaluated must equal ansBase^(1/proposedRootOf) */
    function tryAddWrongChoice(proposedWrongAnswerVal, proposedAnswerStr) {
      var correctAnswer = Math.pow(problem.base, (problem.numerator / problem.denominator));
      if (!doublesEquals(correctAnswer, proposedWrongAnswerVal) ) { // checks out to epsilon that the correct answer and the wrong answer are not equal 
         for (var i = 0; i < wrongVals.length; i++) {
            if (doublesEquals(wrongVals[i], proposedWrongAnswerVal))
              return;
          }
          if (proposedWrongAnswerVal < LARGEST_ALLOWED) {
            wrongVals.push(proposedWrongAnswerVal);
            addWrongChoice(getNicestEvaluation(proposedWrongAnswerVal, proposedAnswerStr));
          }
      }
    }

 
    function showProblem() {
      var exponentStr = '(' + format_fraction(problem.numerator, problem.denominator) + ')';
      write_equation(problem.base + '^' + exponentStr + '= ?');
    }

/* Displays the generalized formula, then the relevant values to plug-in for this problem, then the full evaluation. */
    function generateHints() {
      var hint = '<span class="hint_blue">Generalized formula: \\[ a ^ {1/n} = \\sqrt[n]{a} \\] </span>';
      write_step(hint);
      write_step('<span class="hint_green">Here, \\[ a = ' + problem.base + '\\]</span>');
      write_step('<span class="hint_green">\\[ n = ' + problem.denominator + '\\]</span>');
      var correctAnsStr = '\\sqrt[' + problem.denominator + ']{' + problem.base+ '} '
      var correctAnsVal = Math.pow(problem.base, (problem.numerator / problem.denominator));
      write_step('<span class="hint_blue">So, \\[' + problem.base + '^' + '\\frac{'  + problem.numerator + '}{' + problem.denominator + '} = ' + getNicestEvaluation(correctAnsVal, correctAnsStr) + '\\]</span>');
  } 
}