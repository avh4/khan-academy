var currentexercise ="";
var tries=0;
var correct_at_first_try=false;
var perfectlycorrect = 0; //switched to 1 if the student gets the answer right without hints
var answerChoices = new Array(5);
var answerChoices2 = new Array(5);
var possibleAnswers = new Array(); //These are the possible answers
var possibleAnswers2 = new Array();  //This is used in exercises where the user has to select 2 choices
var definiteWrongAnswers = new Array();
var steps_given=0;
var next_step_to_write =1;
var correctchoice;
var correctchoice2; //used when there are 2 answer choices
var selectedchoice;
var selectedchoice2; 
var starttime = new Date();
var starttimestring = date_to_string(starttime);
var time;
var displaygraph = false;
var alreadyRedirect = 0;
var display_per_step = 1;  //This is how many DIV panes get displayed every time a new hint is given
var timesWrong = 0; //This is used only by words.jsp and new_question()
var recordedProblem = 0;
var recordedCorrect = 0;


var correct = new Image();
correct.src = "/images/face-smiley.gif";
var incorrect = new Image();
incorrect.src = "/images/face-sad.gif";


function checkHistory(compareFunction, entryFunction, termFunction, historyLength)
{
	entryFunction();	
	var recentNums = readCookie(currentexercise+'_'+username);

	//alert([recentNums, term1, term2]);

	if (recentNums!=null)
	{
	
		while (cFunction(recentNums))
		{
			//alert([recentNums, term1, term2]);
			entryFunction();
		}
	}
	else
	{

		recentNums = '';
	}

	var newTerm = termFunction() +'|';

	recentNums = newTerm+recentNums;
	createCookie(currentexercise+'_'+username, recentNums.substring(0,historyLength*newTerm.length), 10);
}

function createCookie(name,value,days) {
	if (days) {
		var date = new Date();
		date.setTime(date.getTime()+(days*24*60*60*1000));
		var expires = "; expires="+date.toGMTString();
	}
	else var expires = "";
	document.cookie = name+"="+value+expires+"; path=/";
}

function readCookie(name) {
	var nameEQ = name + "=";
	var ca = document.cookie.split(';');
	for(var i=0;i < ca.length;i++) {
		var c = ca[i];
		while (c.charAt(0)==' ') c = c.substring(1,c.length);
		if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
	}
	return null;
}

function eraseCookie(name) {
	createCookie(name,"",-1);
}



//To add a choice; assumes correct_answer is already defined
function addWrongChoice(choice)
{
	if(choice!=correct_answer && '`'+choice+'`'!=correct_answer)
		if(!inArray(choice, possibleAnswers) && !inArray(choice, definiteWrongAnswers))
			possibleAnswers.push(choice);
}



function arrayEqual(a,b) //return true if the elements in the array are equal
{
	for(var i=0; i<a.length && i<b.length; i++)
	{
		if (a[i]!=b[i])
			return false;
	}
	return true;
}

function arrayCopy(a)
{
	var c = new Array();
	for(var i=0; i<a.length; i++)
	{
		c.push(a[i]);
	}
	return c;
}

function inArray(item, a)
{
	for(var i=0; i<a.length; i++)
	{
		if(item==a[i])
			return true;
	}
	return false;
}


//get_random() returns a non-zero random number between -10 and 10
function get_random()
{
	var ranNum=Math.round(Math.random()*20)-10; 
	while (ranNum==0) {
		ranNum=Math.round(Math.random()*20)-10;
	}
	return ranNum;
}

function randomIndices(length)
{
	var startArray = new Array();
	var endArray = new Array();
	
	for(var i=0; i<length; i++)
		startArray.push(i);
		
	while(startArray.length>0)
	{
		var epsilon = .99;
		var maxVal = startArray.length-1;
		var index = Math.round(Math.random()*(maxVal+epsilon) - epsilon/2);
		
		endArray.push(startArray.splice(index,1)[0]);
	}

	return endArray;

}

function popup(url)
{
	window.open(url,
		"definition",
		"height=300,width=300,status=no,scrollbars=no, directories=no, resizeable=no, titlebar=no, toolbar=no,menubar=no,location=no");
}

function popVideo(url)
{
	window.open(url,
		"video",
		"height=500,width=450,status=no,scrollbars=no, directories=no, resizeable=no, titlebar=no, toolbar=no,menubar=no,location=no");
}


function popClassroom()
{
	window.open('http://www.khanacademy.org/classroom.jsp',
		"classroom",
		"height=620,width=715,status=no,scrollbars=no, directories=no, resizeable=no, titlebar=no, toolbar=no,menubar=no,location=no");
}

function popExercise(exid)
{
	window.open('http://www.khanacademy.org/exercises/'+exid.substr(0,1)+'/'+exid+'.jsp?nomenu=1',
		"Exercise Sample",
		"height=620,width=715,status=no,scrollbars=yes, directories=no, resizeable=yes, titlebar=no, toolbar=no,menubar=no,location=no");
}


function format_coefficient(number)
{
	if (number==1) {
		return "+"; 
	}
	else if (number==-1) {
		return "-"; 
	}
	else if (number>0) {
		return ("+"+number); 
	}
	else if (number<0) {
		return (""+number); 
	}
	else {
		return ""; 
	}
}

function format_first_coefficient(number)
{
	if (number==-1) {
		return "-"; 
	}
	else if (number==1) {
		return ""; 
	}
	else {
		return (""+number); 
	}
}


//for formatting_constants that aren't the first (when they are first, you can just put the constant there)

function format_constant(number)
{
	if (number>0) {
		return ("+"+number); 
	}
	else if (number<0) {
		return (""+number); 
	}
	else {
		return ""; 
	}
}

function date_to_string(d)
{
	return (""+d.getFullYear()+
		":"+(d.getMonth()+1)+
		":"+d.getDate()+
		":"+d.getHours()+
		":"+d.getMinutes()+
		":"+d.getSeconds());
}

function date_as_string()
{
	var d = new Date();
	return date_to_string(d);
}

function select_choice(choice)
{
	selectedchoice = choice;
}

function select_choice2(choice)
{
	selectedchoice2 = choice;
}

function getGCD(x,y) 
{
	var z;
	while (y!=0) {
		z = x % y;
		x = y;
		y = z;
	}
	return x;
}


function getLCM(x,y)
{
	return (x *y/getGCD(x,y));
}

function format_fraction(n, d)
{
	if (d == 0)
		return "`undefined`";
	if (n == 0)
		return "0";
	var sign = (n/d < 0) ? " - " : "";
	n = Math.abs(n);
	d = Math.abs(d);
	var gcd = getGCD(n, d);
	n = n/gcd;
	d = d/gcd;
	var fraction = sign + n;
	if (d > 1)
		fraction = fraction + "/"+d;
	return fraction;
}

function format_fraction_with_sign(n, d)
{
	var fraction = format_fraction(n,d);
	
	if ((n/d)>0)
	{
		fraction = '+'+fraction;

	}

	return fraction;
}

function format_not_reduced(n,d)
{
	if (n/d < 0)
	{
		return "- "+Math.abs(n)+"/"+Math.abs(d);
	}
	else
	{
		return Math.abs(n)+"/"+Math.abs(d);
	}
}

function format_not_reduced_with_sign(n, d)
{
	var fraction = format_not_reduced(n,d);
	
	if ((n/d)>0)
	{
		fraction = '+'+fraction;
	}
	return fraction;
}

var notDoneType = ''; //This is used by pickType in metautil.js to prevent students from refreshing away a type of problem
var notDoneCookie = '';


function record_problem() //sends ajax request to database to record that problem has been done and presents the 'next question' button
{
	eraseCookie(notDoneCookie);
	
	var endtime = new Date();
	time = endtime.getSeconds()-starttime.getSeconds() +
			60* (endtime.getMinutes() - starttime.getMinutes()) +
			3600* (endtime.getHours() - starttime.getHours());
	
	
	if (tries==0 && steps_given==0)
	{
		correct_at_first_try=true;
		perfectlycorrect=1;
		if (recordedCorrect==0)
		{
			streak++;
			recordedCorrect=1;
		}
		
		//effort=2*effort; //Get double the points for not using hints and getting it right on the first try
		
	}
	else
	{
		perfectlycorrect=0;
		streak = 0;	
		effort = 1;
	}
	
	if (randomMode==1) //You should get more points for problems that are given randomly
	{
		effort =2*effort;
	}
	
	effort = Math.max(effort, 1);

	
	xmlhttp.open('get', '/problemlog.jsp?e='
			+currentexercise
			+'&ts='+timeStamp
			+'&d='+time
			+'&h='+steps_given
			+'&c='+perfectlycorrect
			+'&np='+(energypoints+effort)
			+'&streak='+streak
			+'&mode='+randomMode
			+'&effort='+effort
			+'&t='+tries);		
			
			
	xmlhttp.onreadystatechange = setRecorded;
	xmlhttp.send(null);
	while (recordedProblem==0)
	{
		//do nothing and wait for setRecorded to hit
	}
	
	
	  
}


function setRecorded() {
	recordedProblem=1;
	if (alreadyProficient==0 && streak>=requiredStreak)
	{
		alert("Congratulations! "+streak+" in a row! You will now be forwarded to the main page where you can review your updated knowledge map.");
		window.location = "http://www.khanacademy.org/start.jsp?profex="+currentexercise+"&streak="+streak;
		alreadyRedirect = 1;
	}
}

function processReq() {
	recordedProblem=1;
    if (xmlhttp.readyState == 4) {
        if (xmlhttp.status == 200) {
	 
	  //alert( "everything worked");
	  
	  
	  
	  
        } 
	else {
          //alert( "Not able to log problem" );
	  
	  
	}
    }
}


function check_free_answer()
{
	//alert(correctAnswer);
	if (document.answerform.answer.value==correctAnswer)
	{
		document.images.feedback.src = correct.src;
		if (tries==0 && steps_given==0)
		{
			document.getElementById("correct").value="1"
		}
		//new_question();
		document.getElementById("nextbutton").style.visibility = 'visible';
		
		
	}
	else
	{
		
		tries++;
		document.images.feedback.src= incorrect.src;
		record_problem();
		
	}
}

//For modules that need new colors;
var hColors = ['#D9A326', '#E8887D', '#9CC9B7', '#AE9CC9', '#EAADEA', '#CD8C95', '#EE8262', '#FBA16C', '#DEB887','#CFD784'];
var nColor = "#777777"; //Stands for "normal" color
var curColor =getRandomInt(hColors.length);

function getNextColor()
{
	curColor=(curColor+1)%hColors.length;
	return hColors[curColor];
}


//returns an integer between 0 and max, inclusive
function getRandomInt(max)
{
	var epsilon = .9;
	return Math.round(Math.random()*(max+epsilon) - epsilon/2);
}

function getRandomIntRange(min, max)
{
	var epsilon = .9;
	var x = Math.abs(max-min);
	return (min+Math.round(Math.random()*(x+epsilon) - epsilon/2));
}

function check_answer()
{
	if (selectedchoice === undefined) 
	{
			window.alert("Please choose your answer.");
			return;
	}

	if (selectedchoice==correctchoice)
	{
		if (tries==0 && steps_given==0)
		{
			document.getElementById("correct").value="1"
		}
		document.images.feedback.src = correct.src;
		//new_question();
		document.getElementById("nextbutton").style.visibility = 'visible';
		eraseCookie(notDoneCookie);
		
		
	}
	else
	{
		tries++;
		document.images.feedback.src= incorrect.src;
		
	}
}

//for problems where the user can give 2 answers
function check_both_answers()
{
	if (selectedchoice === undefined || selectedchoice2 === undefined) 
	{
			window.alert("Please choose both answers.");
			return;
	}

	if (selectedchoice==correctchoice  && selectedchoice2==correctchoice2)
	{
		document.getElementById("nextbutton").style.visibility = 'visible';
		document.images.feedback.src = correct.src;
		if (tries==0 && steps_given==0)
		{
			document.getElementById("correct").value="1"
		}
	}
	else
	{
		tries++;
		document.images.feedback.src= incorrect.src;
	
	}
}


function array_sum(a) {

	var sum=0;
	for (var i=0; i<a.length; i++) {
		sum+=a[i];
	}
	return sum;
}

function start_random_problem()
{
	window.location = randomProblem();
}

function write_step(text, step) //Deprecated
{
	document.write('<P><div id=\"step'+step+'_'+display_per_step+'\" style=\"position:relative; visibility:hidden;\"><font face=\"arial\" size=3>'+text+'</font></div></P>');
}

function write_step(text)
{
	document.write('<P><div id=\"step'+next_step_to_write+'_'+display_per_step+'\" style=\"position:relative; visibility:hidden;\"><font face=\"arial\" size=3>'+text+'</font></div></P>');
	next_step_to_write++;
}

//this is used in lineq.jsp
function write_table_step(left, right)
{
	document.write(	'<tr><td align=right>'
			+get_step_part_string('`'+left+'`', next_step_to_write, 1)
			+'</td><td align=left class=\"nobr\"><nobr>'
			+get_step_part_string('`='+right+'`', next_step_to_write, 2)
			+'</nobr></td></tr>');
	next_step_to_write++;
}

function table_step_header(left, right)
{
	document.write('<center><table border=0 width=100%><tr><td><img src="/images/blank.gif" height=1 width=200"></td><td><img src="/images/blank.gif" height=1 width=200"></td></tr><tr><td align=right><font face=\"arial\" size=4>`'+
			left+
			'</font></td><td align=left class=\"nobr\"><nobr><font face=\"arial\" size=4 class=\"nobr\">`='+right+'`</font></nobr></td></tr>');	
}

function write_table_step(explanation, left, right)
{
	document.write(	'<tr><td align=left class=\"nobr\">'
			+get_step_part_string('<FONT class=\"explanation\"  class=\"nobr\">'+explanation+'</font>', next_step_to_write, 3)
			+'</td><td align=right class=\"nobr\"><nobr>'
			+get_step_part_string('`'+left+'`', next_step_to_write, 1)
			+'</nobr></td><td align=left class=\"nobr\"><nobr>'
			+get_step_part_string('`='+right+'`', next_step_to_write, 2)
			+'</nobr></td></tr>');
	next_step_to_write++;
}

function table_step_header(explanation, left, right)
{
	document.write('<center><table border=0><tr><td><img src="/images/blank.gif" height=1 width=200"></td><td><img src="/images/blank.gif" height=1 width=200"></td><td><img src="/images/blank.gif" height=1 width=200"></td></tr><tr><td align=left><font face=\"arial\" size=4  class=\"nobr\">'+explanation+'</font></td><td align=right><font face=\"arial\" size=4>`'+
			left+
			'</font></td><td align=left class=\"nobr\"><nobr><font face=\"arial\" size=4  class=\"nobr\">`='+right+'`</font></nobr></td></tr>');	
}

function table_step_footer()
{
	document.write('</table></center>');
}

function get_step_part_string(text, present_step, part)
{
	return ('<div id=\"step'+present_step+'_'+part+'\" style=\"position:relative; visibility:hidden;\"><font face=\"arial\" size=4>'+text+'</font></div>');
}

function write_equation(equation)
{
	document.write('<p><font face=\"arial\" size=4><center>`'+equation+'`</center></font></p>');
}

function write_text(text)
{
	document.write('<p><font face=\"arial\" size=3>'+text+'</font></p>');
}

function equation_string(equation)
{
	return ('<p><font face=\"arial\" size=4><center>`'+equation+'`</center></font></p>');
}

function problem_header()
{
	document.write('<table width=100%><tr><td valign=top width=70%>');
}

//used in lineq.jsp
function get_eq_step_string(instruction, lside, rside)
{
	return('<tr><td>'+instruction+'</td><td>`'+lside+'='+rside+'`</td></tr>');	
}


function perfect_square_factor(n)  //only factors numbers up to 625
{
	var square_factor=1;

	for (var i=1; (i<25 && i<Math.abs(n)); i++)
	{
		//document.write('<p>'+n+" "+i+" "+(Math.abs(n)%(i*i))+'</p>');
		if ((Math.abs(n)%(i*i))==0)
		{
			square_factor=i*i;
		}
	}
	//alert("N:"+n+",Factor:"+square_factor);


	if (Math.abs(square_factor)==1) //the number is not factorable has the product of a perfect square and another number
	{
		return [n];
	}
	else
	{
		return [n/square_factor, square_factor];
	}
}

function problem_footer()
{
	//randomly determine which choice will be the correct choice, the math is funky to ensure an equal probability of being any number from 0-4 inclusive
	correctchoice = Math.round(Math.random()*4.98-.49);
	if (displaygraph)
	{
		document.write('</td><td valign=\"top\"><embed align=\"left\" width=260 height=260 src=\"/d.svg\" script=\'graph_update()\'><form name=\"answerform\">');
	}
	else
	{
		document.write('</td><td valign=\"top\"><form name=\"answerform\">');
	}
	
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
			/****
			var new_index = Math.round(Math.random()*(possibleAnswers.length-.02)-.49); //where to pick the new wrong choice
			var new_wrong_choice = possibleAnswers.splice(new_index, 1)[0];
			answerChoices[i]='`'+new_wrong_choice+'`';
			*****/
		}

		document.write('<br><input type=\"radio\" name=\"selectAnswer\" onClick=\"select_choice('+i+')\">'+answerChoices[i]+'</input></br>');

	}

	document.write('<br><input type=\"button\" value=\"Hint\" onClick=\"give_next_step()\"><input type=\"button\" value=\"Check Answer\" onClick=\"check_answer()\"></br>');
	document.write('<br><img src=\"/images/blank.gif\" name=\"feedback\"><div id=\"nextbutton\" style=\"position:relative; visibility:hidden;\"><input type=\"button\" value=\"Correct! Next Question...\" onClick=\"new_question()\"></div></br>');
	document.write('</form></td></tr></table>');	
	document.answerform.reset();
}

//for problems where the user has to select 2 answers
function double_answer_footer()
{
	//randomly determine which choice will be the correct choice, the math is funky to ensure an equal probability of being any number from 0-4 inclusive
	correctchoice = Math.round(Math.random()*4.98-.49);
	correctchoice2 = Math.round(Math.random()*4.98-.49); //every variable with a 2 is for the second set of choices
	if (displaygraph)
	{
		document.write('</td><td valign=\"top\"><embed align\"right\" width=200 height=200 src=\"d.svg\" script=\'graph_update()\'><form name=\"answerform\">');
	}
	else
	{
		document.write('</td><td valign=\"top\"><form name=\"answerform\">');
	}
	
	//Fill in the choices
	//need to fix it so that the other choices can never be the same as the correct choice
	document.write('<table border=0>');
	for (var i=0; i<5; i++)
	{
		if (i==correctchoice) 
		{
			answerChoices[i]=correct_answer;
		}
		else
		{
			
			var new_index = Math.round(Math.random()*(possibleAnswers.length-.02)-.49); //where to pick the new wrong choice
			var new_wrong_choice = possibleAnswers.splice(new_index, 1)[0]
			answerChoices[i]='`'+new_wrong_choice+'`';
		}
		if (i==correctchoice2) 
		{
			answerChoices2[i]=correct_answer2;
		}
		else
		{
			
			var new_index = Math.round(Math.random()*(possibleAnswers2.length-.02)-.49); //where to pick the new wrong choice
			var new_wrong_choice = possibleAnswers2.splice(new_index, 1)[0]
			answerChoices2[i]='`'+new_wrong_choice+'`';
		}
		document.write('<tr><td><input type=\"radio\" name=\"selectAnswer\" onClick=\"select_choice('+i+')\">'+answerChoices[i]
			+'</input></td><td><input type=\"radio\" name=\"selectAnswer2\" onClick=\"select_choice2('+i+')\">'+answerChoices2[i]+'</input></td></tr>');

	}

	document.write('</table>')
	
	document.write('<br><input type=\"button\" value=\"Hint\" onClick=\"give_next_step()\"><input type=\"button\" value=\"Check Answer\" onClick=\"check_both_answers()\"></br>');
	document.write('<br><img src=\"/images/blank.gif\" name=\"feedback\"><div id=\"nextbutton\" style=\"position:relative; visibility:hidden;\"><input type=\"button\" value=\"Correct! Next Question...\" onClick=\"new_question()\"></div></P>');
	document.write('</form></td></tr></table>');	
	document.answerform.reset();
}

function checkAnswerWithReturn(event)
{
	if (event &&event.which==13)
		check_free_answer();
	else
		return true;
}


function free_answer_footer()
{
	document.write('</td><td valign=\"top\"><form name=\"answerform\">');
	document.write('<br>Answer:<input type=\"text\" size=10 id=\"answer\" name=\"answer\"></br>');
	document.write('<br><input type=\"button\" value=\"Hint\"  onClick=\"give_next_step()\">');
	document.write('<input type=\"button\" value=\"Check Answer\" onClick=\"check_free_answer()\"></br>');
	document.write('<br><img src=\"/images/blank.gif\" name=\"feedback\"><div id=\"nextbutton\" style=\"position:relative; visibility:hidden;\"><input type=\"button\" value=\"Correct! Next Question...\" onClick=\"new_question()\"></div></br>');
	document.write('</form></td></tr></table>');
	document.answerform.reset();
}




