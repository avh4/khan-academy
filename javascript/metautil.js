var correctAnswer = null;
var correct_answer = null;
var comparisonFunction = function eq(a,b) { return a==b; }


//Returns n rounded to "precision" places behind the decimal point
function roundNumber(n, precision)
{
	return Math.round(n*Math.pow(10,precision))/Math.pow(10,precision);	
}

//Randomly choose a problem type



function pickType(low,high)
{
	
	notDoneCookie = currentexercise+'_'+username+'_lasttype';
	
	notDoneType = readCookie(notDoneCookie);
	
	if (notDoneType==null || notDoneType=='')
	{
		notDoneType = ''+getRandomIntRange(low, high);
	}
	eval("type"+notDoneType+"()");
	
	createCookie(notDoneCookie, notDoneType, 10);
}

function pickNumber(low,high)
{
	
	var notDoneCookie = currentexercise+'_'+username+'_lasttype';
	
	var notDoneType = readCookie(notDoneCookie);
	
	if (notDoneType==null || notDoneType=='')
	{
		notDoneType = ''+getRandomIntRange(low, high);
	}
	
	createCookie(notDoneCookie, notDoneType, 5);
	a
	return notDoneType;
}






function writeText(text)
{
	write_text(text);
}

function writeStep(step)
{
	write_step(step);
}


function simplifiedRoot(x)
{
	var factor = perfect_square_factor(x);
	if (factor.length==1)
	{
		return 'sqrt('+x+')';
	}
	else if (factor[0]==1)
	{
		return Math.sqrt(x);
	}
	else 
	{
		return (Math.sqrt(factor[1])+'sqrt('+factor[0]+')');
	}
}



function equationString(s)
{
	return equation_string(s);
}

function writeEquation(e)
{
	writeText(equationString(e));
}

function problemHeader(name)
{
	currentexercise = name;
	problem_header();
}

function setCorrectAnswer(a)
{
	correctAnswer = a+'';
	correct_answer = a;
}


function mathFormat(e)
{
	return	'`'+e+'`';
}

function nonZeroRandomInt(l,h)
{
	var i = getRandomIntRange(l,h);
	while (i==0)
		i = getRandomIntRange(l,h);
	return i;
}

function problemFooter()
{
	while (possibleAnswers.length<6)
	{
		addWrongChoice(getRandomIntRange(-10,10));
	}
	correct_answer = mathFormat(correct_answer);
	
	
	problem_footer();
}

function freeAnswerFooter()
{
	free_answer_footer();
}

function formatCoefficient(c)
{
	return format_coefficient(c);
}

function formatFirstCoefficient(c)
{
	return format_first_coefficient(c);
}

function formatConstant(c)
{
	return format_constant(c);
}

function formatFraction(n,d)
{
	return format_fraction(n,d);
}

function formatFractionWithSign(n,d)
{
	return format_fraction_with_sign(n,d);
}

function formatNotReduced(n,d)
{
	return format_not_reduced(n,d);
}

function formatNotReducedWithSign(n,d)
{
	return format_not_reduced_with_sign(n,d);
}


function arraySum(a)
{
	return array_sum(a);
}


function checkFreeAnswer()
{
	
	if (parseFloat(document.getElementById("answer").value)==parseFloat(correctAnswer))
	{
		
		if (tries==0 && steps_given==0)
		{
			document.getElementById("correct").value="1"
		}
		document.getElementById("nextbutton").style.visibility = 'visible';
		;
		document.images.feedback.src = correct.src;
		eraseCookie(notDoneCookie);
		document.forms['answerform'].correctnextbutton.focus()
	}
	else
	{
		
		tries++;
		document.images.feedback.src= incorrect.src;
	}
	
}

function graphFooter()
{
	correct_answer = mathFormat(correct_answer);
}


function graphicalFooter()
{

	correct_answer = mathFormat(correct_answer);
	correctchoice = Math.round(Math.random()*4.98-.49);

	//Fill in the choices
	//need to fix it so that the other choices can never be the same as the correct choice
	
	var possibleWrongIndices=randomIndices(possibleAnswers.length);
	var definiteWrongIndices=randomIndices(definiteWrongAnswers.length);
	for (var i=0; i<5; i++)
	{
		if (i==correctchoice) 
		{
			answerChoices[i]=correct_answer;
		}
		else
		{
			if (definiteWrongIndices.length>0)
			{
				answerChoices[i]='`'+definiteWrongAnswers[definiteWrongIndices.pop()]+'`';
			}
			else
			{
				answerChoices[i]='`'+possibleAnswers[possibleWrongIndices.pop()]+'`';
			}
		}

		document.write('<br><input type=\"radio\" name=\"selectAnswer\" onClick=\"select_choice('+i+')\">'+answerChoices[i]+'</input></br>');

	}

	document.write('<br><input type=\"button\" value=\"Hint\" onClick=\"give_next_step()\"><input type=\"button\" value=\"Check Answer\" onClick=\"check_answer()\"></br>');
	document.write('<br><img src=\"http://www.khanacademy.org/images/blank.gif\" name=\"feedback\"><div id=\"nextbutton\" style=\"position:relative; visibility:hidden;\"><input type=\"button\" value=\"Correct! Next Question...\" onClick=\"new_question()\"></div></br>');
	document.write('</form></td></tr></table>');	
	document.answerform.reset();
}





