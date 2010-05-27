

var correctAnswer = null;
var correct_answer = null;
var possibleAnswers = new Array();
var wrongAnswers = new Array();



function header()
{
	document.write('<table width=100%><tr><td valign=top width=70%>');
}


function footer()
{
	//randomly determine which choice will be the correct choice, the math is funky to ensure an equal probability of being any number from 0-4 inclusive
	correctchoice = Math.round(Math.random()*4.98-.49);
	document.write('</td><td valign=\"top\"><form name=\"answerform\">');
	
	//Fill in the choices
	//need to fix it so that the other choices can never be the same as the correct choice
	
	var possibleWrongIndices=randomIndices(possibleAnswers.length);
	for (var i=0; i<5; i++)
	{
		if (i==correctchoice) 
		{
			answerChoices[i]=correct_answer;
		}
		else
		{
			answerChoices[i]=possibleAnswers[possibleWrongIndices.pop()];
		}

		document.write('<br><input type=\"radio\" name=\"selectAnswer\" onClick=\"select_choice('+i+')\">'+answerChoices[i]+'</input></br>');

	}

	document.write('<br><input type=\"button\" value=\"Hint\" onClick=\"give_next_step()\"><input type=\"button\" value=\"Check Answer\" onClick=\"check_answer()\"></br>');
	document.write('<br><img src=\"/images/blank.gif\" name=\"feedback\"><div id=\"nextbutton\" style=\"position:relative; visibility:hidden;\"><input type=\"button\" value=\"Correct! Next Question...\" onClick=\"new_question()\"></div></br>');
	document.write('</form></td></tr></table>');	
	document.answerform.reset();
}




