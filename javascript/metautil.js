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
	var notDoneType = null;
	generateNewProblem(function () {
		notDoneType = ''+getRandomIntRange(low, high);
		return notDoneType;
	}, Math.floor((high-low)/2), "type");
	eval("type"+notDoneType+"()");
}

function pickNumber(low,high)
{
	var notDoneNum = null;
	generateNewProblem(function () {
		notDoneNum = getRandomIntRange(low, high);
		return ''+notDoneNum;
	}, Math.floor((high-low)/2), "number");
	return notDoneNum;
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

function setCorrectAnswer(a)
{
	correctAnswer = a+'';
	correct_answer = a;
}


function mathFormat(e)
{
	// Make it a string
	e = e + ''; 
	// If it is already ASCIIMath, leave it alone
	if (e.length > 0 && e.charAt(0) == '`')
		return e;
	// Normalize the formatting if it is an integer
	var intVal = parseInt(e);
	if (!isNaN(intVal))
		e = format_fraction(intVal,1);
	// Make it ASCIIMath
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

var correctnessRegistered = false;
function handleCorrectness(isCorrect)
{
	if (!correctnessRegistered) 
	{
		// Attempt to register the correctness of the answer with the server, before telling the user 
		// whether it is correct.  This prevents the user from just reloading the page to quickly and quietly 
		// avoid blowing a streak when he gets a wrong answer.  If the attempt to register the correctness fails,
		// we don't worry about it because they might just be having connectivity problems or need to log in again.
		// That means it is still possible for a user to cheat (e.g. by logging out before clicking "Check Answer")
		// but it takes longer and is more noticeable.
		$.post("/registercorrectness", 
			{
				key: document.getElementById("key").value,
				time_warp: document.getElementById("time_warp").value,
				correct: ((isCorrect && tries==0 && steps_given==0) ? 1 : 0)
			}); // Fire and forget, no callback.
		correctnessRegistered = true;		
	}	
	if (isCorrect)
	{
		
		if (tries==0 && steps_given==0)
		{
			document.getElementById("correct").value="1"
		}
		document.getElementById("nextbutton").style.visibility = 'visible';
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

function checkFreeAnswer()
{
	var usersAnswer = parseFloat(document.getElementById("answer").value);
	if (isNaN(usersAnswer)) 
	{
			window.alert("Your answer is not a number.  Please try again.");
			return;
	}
	var isCorrect = (usersAnswer==parseFloat(correctAnswer));

	handleCorrectness(isCorrect);
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
	document.write('<br><img src=\"/images/blank.gif\" name=\"feedback\"><div id=\"nextbutton\" style=\"position:relative; visibility:hidden;\"><input type=\"button\" value=\"Correct! Next Question...\" onClick=\"new_question()\"></div></br>');
	document.write('</form></td></tr></table>');	
	document.answerform.reset();
}

function getResponseProps(response, header){
	try {
		var s = response.getResponseHeader(header || 'X-Ajax-Props');
		if (s==null || s=="")
			return new Object()
		else
			return eval("o="+s)
	} catch (e) { return new Object() }
}

KhanAcademy = {
	onMathMLSupportReady: function(callbackWhenReady) {
		ASCIIMathMLTranslate = translate;
		translate = function(callback) {
			ASCIIMathMLTranslate();
			if (callback && callback.call)
				callback.call();
		};
		// Use MathJax only if the browser doesn't support MathML or
		// doesn't have reasonable fonts installed
		if (browserSupportsMathML() && browserHasUsableFont()) {
			callbackWhenReady.call();
			return;			
		}
		checkForMathML = false;
		showasciiformulaonhover = false;
		translate = function(callback) {
			var hintButton = $('#hint');
			if (hintButton) {
				hintButton.attr('disabled', 'disabled');				
			}
			ASCIIMathMLTranslate();
			function enableHintAndMakeCallback() {
				if (hintButton)
					hintButton.removeAttr('disabled');
				if (callback && callback.call)
					callback.call();
			}
			if (MathJax.isReady)
				MathJax.Hub.Queue(["Typeset",MathJax.Hub,null,enableHintAndMakeCallback]);
			else
				enableHintAndMakeCallback();
		};
		// When MathJax has finished starting up, translate the page.
		MathJax.Hub.Register.StartupHook("End", callbackWhenReady);
		
		function browserHasUsableFont() {
			var d = new Detector();
			var usableFonts = ['cmsy10',
				'STIXNonUnicode', 
				'STIXSize1', 
				'STIXGeneral', 
				'Standard Symbols L', 
				'DejaVu Sans', 
				'Cambria Math']; 
			for (var i = 0; i < usableFonts.length; i++) {
	 			if (d.test(usableFonts[i])) {
					return true;
				}		
			}
			return false;
		}
		
		function browserSupportsMathML() {
			var MathPlayer; 
			try {
				new ActiveXObject("MathPlayer.Factory.1"); 
				MathPlayer = true;
			} catch(err) {
				MathPlayer = false
			};
			return (($.browser.mozilla && versionAtLeast("1.5")) ||
                  		($.browser.msie && MathPlayer) ||
                  		($.browser.opera && versionAtLeast("9.52")));
				
			function versionAtLeast(minVersion) {
				var actualVersion = $.browser.version.split(".");
				minVersion = minVersion.split(".");
				while (minVersion.length && actualVersion.length) {
					var minV = minVersion.shift();
					var actualV = actualVersion.shift();
					if (actualV > minV) 
						return true;
					if (actualV < minV) 
						return false;
				}
				return false;
			}
		}
	}
};
