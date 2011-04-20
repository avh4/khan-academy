var Exercise = {
    fWriteToDoc: true,
    fSupportsAjax: false,
    fRegisteringAnswer: false,
    fAddNoneOfThese: true,
    fExtendsMultipleChoice: false,
    
    showNextProblem: function() {},
    
    init: function() {
        this.tries=0;
        this.possibleAnswers = new Array(); //These are the possible answers
        this.possibleAnswers2 = new Array();  //This is used in exercises where the user has to select 2 choices
        this.checkboxChoices = new Array(); //THis is used in exercises with checkbox answers
        this.steps_given=0;
        this.next_step_to_write =1;
        this.correctchoice;
        this.correct = new Image();
        this.correct.src = "/images/face-smiley.gif";
        this.incorrect = new Image();
        this.incorrect.src = "/images/face-sad.gif";
    },
    
    display: function() {
        // set vals to 0 after document is ready
        $("#correct").val(0);
        $("#hint_used").val(0);
        Exercise.enable();
        
        if (this.fSupportsAjax) {
            if (window.svgedit && svgedit.clearScratchpad) 
                svgedit.clearScratchpad();
        
            $("#question_content").attr("id", "old_question_content");
            $("#question_content_container").append("<div id=\"question_content\" style=\"position:relative; float: left\"></div>");
            $("#question_content").css("left", 1000);
        }
        
        this.showNextProblem();
        translate();
        
        if (this.fExtendsMultipleChoice) {
            $("#answer_content").html("");
            renderChoices();
        } else
            $("#answer").val("")
            
        translate();
        
        if (this.fSupportsAjax) {
            $("#old_question_content").animate({"left": -500}, 250, function() {
                $("#old_question_content").remove();
                $("#question_content").animate({"left": 0}, 250);    
            });
        }
    },
    
    enable: function() {
        Exercise.fRegisteringAnswer = false;
        $("#next-question-button").removeClass("buttonDisabled").removeAttr("disabled");
        Exercise.showThrobber(false);
    },
    
    disable: function() {
        Exercise.fRegisteringAnswer = true;
        $("#next-question-button").addClass("buttonDisabled").attr("disabled", "disabled");
        setTimeout(function() { Exercise.showThrobber(true); }, 10);
    },
    
    submitForm: function() {
        if (this.fSupportsAjax) {
            var data = {};
            $.each(["exid", "key", "correct", "problem_number", "start_time", "hint_used", "time_warp"], function() {
              data[this] = $("#" + this).val();
            });
            
            Exercise.disable();

            $.ajax({
                type: "GET",
                url: "/registeranswer",
                data: data,
                success: this.finishRegisterAnswer,
                error: this.error
            });
        } else
            $("#answerform").submit();
    },
    
    finishRegisterAnswer: function(response) {
        try {
            eval("var data=" + response);
            KhanAcademy.updateSeed(data.problem_number);
            Exercise.init();
            Exercise.display();
            Exercise.resetFeedback();
            Exercise.updateUserData(data);
        } catch (err) {
            Exercise.error();
        }
    },
    
    error: function() {
        // try page-reload on ajax error
        window.location.reload();
    },
    
    resetFeedback: function() {
        $("#check-answer-button").show();
        $("#next-container").hide();
        $("#feedback").hide();
        correctnessRegistered = false;
    },
    
    updateUserData: function(data) {
        $("#user-points-container").html(data.user_points_html);
        $("#start_time").val(data.start_time);
        $("#problem_number").val(data.problem_number);

        var link = $("#report-problem").attr("href");
        link = link.substr(0, link.indexOf("Problem-")) + "Problem-" + data.problem_number;
        $("#report-problem").attr("href", link);
        $("#time_warp").val(data.time_warp);
        $("#streak").val(data.streak);
        $("#exercise-points").html(data.exercise_points);    

        $("#streak-bar-container").html(data.streak_bar_html);
        $("#exercise-icon-container").html(data.exercise_icon_html);

        var curr_message = $("#exercise-message-container").html();
        if (data.exercise_message_html && curr_message != data.exercise_message_html) {
            $("#exercise-message-container").hide();
            $("#exercise-message-container").html(data.exercise_message_html);
            $("#exercise-message-container").slideDown();    
        } else if (!data.exercise_message_html) {
            $("#exercise-message-container").html("")
        }
        
        $("#badge-count-container").html(data.badge_count_html);
        
        $("#badge-notification-container").html("");
        $("#badge-notification-container").hide();
        if (data.badge_notification_html) {
            $("#badge-notification-container").html(data.badge_notification_html)
            Badges.show()
        }
    
    },
    
    getNumPossibleAnswers: function() {
        return this.possibleAnswers.length;
    },
    
    showThrobber: function (fVisible) {
        if (Exercise.fRegisteringAnswer && fVisible)
            $("#throbber").show();
        else
            $("#throbber").hide();
    }
};

var selColor = "#AE9CC9";
var noSelColor = "#333333";

// Deprecated: Use generateRandomProblem (below) instead.
// Note: compareFunction is now ignored.  entryFunction must return the same
// id for all problems that should be considered equivalent.
function checkHistory(compareFunction, entryFunction, termFunction, historyLength)
{
	generateNewProblem(function () {
		entryFunction();
		return termFunction();
	}, historyLength/2);
}

// Calls randomProblemGenerator until it returns a problem id that hasn't been used recently. 
function generateNewProblem(randomProblemGenerator, range, salt)
{
	/*
	 * To generate reproducible problems P_0, P_1, P_2, ... with no repeats 
	 * within R problems:
	 * 1. Let U(S, {problems_to_avoid}) be a problem generated from seed S that is not 
	 *    in the set {problems_to_avoid}.  So it is "unique" relative to {problems_to_avoid}.
	 * 2. Then, we can generate a reproducible sequence of R problems with no
	 *    repeats given a seed S.  Call those generated problems G(0, S) through G(R-1, S).
	 *    They can be produced iteratively:
	 *    G(0, S) = U(S, {})
	 *    G(j, S) = U(S, {G(0, S),...G(j-1,S)})
	 * 3. We can use G to compute half of the P_i, by dividing the P_i into groups of R
	 *    problems and using G to compute every other group.  So:
	 *    For (i%(2R)) < R, let P_i = G(i%(2R), s(i//(2R)))
	 *       where "//" is integer division without remainder and
	 *       s(x) is the seed function that depends only on i through its parameter
	 *       and ideally ensures that s(x)!=s(y) for all x!=y.  s(x) = x could work.
	 *       So could s(x) = x+username if we wanted different users to get different
	 *       problems.
	 *    That covers half of the problems, specifically the 1st, 3rd, 5th, etc groups 
	 *    of R problems.
	 * 4. For the problems in the remaining (even) groups, we need to ensure that they 
	 *    don't match the problems that are within a distance of R in either the previous
	 *    or next group.  To do that, we generate the relevant problems from those groups
	 *    (which requires only knowing the problem numbers) and then use U() to ensure we
	 *    don't duplicate them.  So:
	 *    For (i%(2R)) >= R, let P_i = U(s(i//(2R)), {P_j where |j-i| < R})
	 *    
	 * From an implementation perspective, to generate P_i:
	 *   if (i%(2R)) < R):
	 *     Generate the first problem in its group, number (i//(2R))*2R, and subsequent problems up to
	 *     and including P_i skipping duplicates.
	 *   else:
	 *     Generate the first problem in the next group, number ((i//(2R))+1)*2R, and subsequent problem
	 *     numbers < i+R, skipping duplicates.
	 *     Generate all the problems in the previous group, starting with number (i//(2R)-1)*2R, skipping
	 *     duplicates within that group.
	 *     Generate the first problem in its group, number (i//(2R))*2R, and subsequent problems up to
	 *     and including P_i skipping duplicates in that group and in the problems in adjacent groups with
	 *     numbers within R of i.
	 */
	if (!range)
		range = 10;
	range = Math.floor(range);
	if (!salt)
		salt = '';
	var i = KhanAcademy.problem_number;
	var R = range;
	var group = Math.floor(i/R);
	var prev_group_problems = [];
	var next_group_problems = [];
	if (group % 2 == 1) {
		// generate problems to avoid
		KhanAcademy.seedRandom(s(group-1));
		for (var j=0; j<R; j++) {
			prev_group_problems.push(U(prev_group_problems));			
		}
		KhanAcademy.seedRandom(s(group+1));
		for (var j=0; j<(i%R); j++) {
			next_group_problems.push(U(next_group_problems));			
		}
	}
	
	KhanAcademy.seedRandom(s(group));
	var p = group*R;
	var current_group_problems = [];
	while (p <= i) {
		var problems_to_avoid = current_group_problems.concat(prev_group_problems.slice(p%R), next_group_problems.slice(0,p%R));
		current_group_problems.push(U(problems_to_avoid));
		p++;
	}
	
	function s(x) {
		return ''+salt+x;
	}
	
	function U(avoidance_arr) {
		var id;
		// We only try 10 times to prevent buggy callers
		// from generating an infinite loop if their randomProblemGenerator
		// always returns true.  See:
		// http://code.google.com/p/khanacademy/issues/detail?id=49
		var tries = 0;
		while(tries < 10 && $.inArray(id = randomProblemGenerator(), avoidance_arr) != -1) {
			tries++;			
		}
		return id;
	}
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

function equivInArray(target, arr) {
	for (var i = 0; i < arr.length; i++) {
		if (mathFormat(target) == mathFormat(arr[i]))
			return true;
	}
	return false;
}

//To add a choice; assumes correct_answer is already defined
function addWrongChoice(choice)
{
	if(mathFormat(choice) != mathFormat(correct_answer))
		if(!equivInArray(choice, Exercise.possibleAnswers))
			Exercise.possibleAnswers.push(choice);
}

function renderChoices() {
	var num_choices = Math.min(1 + Exercise.possibleAnswers.length, 5);
	var answerChoices = new Array(num_choices);
	Exercise.correctchoice = Math.round(KhanAcademy.random()*(num_choices - 0.02)-.49);

	var possibleWrongIndices = randomIndices(num_choices - 1);

	for (var i = 0; i < num_choices; i++) {
    	if (i == Exercise.correctchoice)
		    answerChoices[i] = '`' + correct_answer + '`';		    
		else
			answerChoices[i] = '`' + Exercise.possibleAnswers[possibleWrongIndices.pop()]+'`';			    
	}
	
	if(Exercise.fAddNoneOfThese) {
        // With probability 1/4, the correct answer is "None of these"
    	if (!getRandomIntRange(0, 3)) {
            answerChoices[Exercise.correctchoice] = answerChoices[num_choices - 1]	   
            Exercise.correctchoice = num_choices - 1; 
    	}
    	answerChoices[num_choices - 1] = "None of these";	    
	}

    // if you need to rearrange order or answers implement preDisplay function in derived html
    if (window.preDisplay)
        preDisplay(answerChoices, Exercise.correctchoice);

	for (i = 0; i < num_choices; i++) {
       appendAnswerHtml('<p style="white-space:nowrap;margin-top:10px;"><label for="answerChoice'+i+'"><input type="radio" id="answerChoice'+i+'" name="selectAnswer" class="select-choice" tabindex="'+(i+1)+'" data-choice="'+i+'">&nbsp;'+answerChoices[i]+'</input></label></p>');
    }
    
    $('.select-choice').keypress(function(e) {
        if (e.which == '13') {
            check_answer_block();
            return false;
        }
    });
}

//To add choices in checkbox-based problems
function addCorrectCheckboxChoice(choice){
    Exercise.checkboxChoices.push([choice, true]);
}

function addIncorrectCheckboxChoice(choice){
    Exercise.checkboxChoices.push([choice, false]);
}

function getNumPossibleAnswers() {
    return Exercise.possibleAnswers.length;
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
	var ranNum=Math.round(KhanAcademy.random()*20)-10; 
	while (ranNum==0) {
		ranNum=Math.round(KhanAcademy.random()*20)-10;
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
		var index = Math.round(KhanAcademy.random()*(maxVal+epsilon) - epsilon/2);
		
		endArray.push(startArray.splice(index,1)[0]);
	}

	return endArray;

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

function format_string_with_color(str, color) {
    return "<span style='color: " + color + "'>" + str + "</span>"
}

function format_math_with_color(str, color) {
    return format_string_with_color("`" + str + "`", color);
}

function format_expression(coeff, str, color, is_leading) {
    var expression = '';
	for (var i = 0; i < coeff.length; i++) {
        if (i == 0)
            expression += '<font color=\"'+ color +'\">`';
        if (i == 0 && is_leading) {
            if (str == '')
                expression += coeff[i]
            else
                expression += format_first_coefficient(coeff[i]) + " " + str + " " ;
        } else {
            if (!str)
                expression += format_constant(coeff[i])
            else
		        expression += format_coefficient(coeff[i]) + " " + str + " ";
    	}
    }
   if (expression)
        expression += '`</font>';
        
    return expression;
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

function format_fraction_first_coefficient(n, d)
{
	var ffc = format_fraction(n, d);

	if (ffc == '1') {
	   	return '';
	} else if (ffc == '-1') {
	       	return '-';
	} else {
	        return ffc;
	}
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

function convertDegreeToRadian(degree) {
    return degree * Math.PI / 180;
}

function convertRadianToDegree(radian) {
    return radian * 180 / Math.PI;
}

// sample usage: rotateVector([1, 0], 90) ==> [0, 1]
function rotateVector(vector, degree) {
    var cos = Math.cos(convertDegreeToRadian(degree));
    var sin = Math.sin(convertDegreeToRadian(degree));
    
    var new_x = (vector[0] * cos) - (vector[1] * sin);
    var new_y = (vector[0] * sin) + (vector[1] * cos);
    
    return [roundToHundredth(new_x), roundToHundredth(new_y)];
}

function roundToHundredth(num) {
    return Math.round(num * 100) / 100;
}

var notDoneType = ''; //This is used by pickType in metautil.js to prevent students from refreshing away a type of problem
var notDoneCookie = '';


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
	return Math.round(KhanAcademy.random()*(max+epsilon) - epsilon/2);
}

function getRandomIntRange(min, max)
{
	var epsilon = .9;
	var x = Math.abs(max-min);
	return (min+Math.round(KhanAcademy.random()*(x+epsilon) - epsilon/2));
}

function randomFromArray(a)
{
	var index = getRandomIntRange(0, a.length-1);
	return a[index];
}

function check_answer()
{
    var checkedIndex = $(":radio[name='selectAnswer']").index($(":radio[name='selectAnswer']:checked")); 
    
    if (checkedIndex == -1) {
        window.alert("Please choose your answer.");
        return;
    }
    
	var isCorrect = (checkedIndex == Exercise.correctchoice)
	handleCorrectness(isCorrect);
}

function randomizeCheckboxChoices(){
    var randomizedCheckboxChoices = [];
    while(Exercise.checkboxChoices.length > 0){
        randomizedCheckboxChoices.push(Exercise.checkboxChoices.splice(getRandomIntRange(0, Exercise.checkboxChoices.length - 1), 1)[0]);
    }
    Exercise.checkboxChoices = randomizedCheckboxChoices;
}

function generateCheckboxAnswerArea(){
    randomizeCheckboxChoices();
    for(var i=0; i < Exercise.checkboxChoices.length; i++){
        var checkbox_name = 'selectAnswerCheckbox_'+i; //Has to match the value used in checkCheckboxChoices
        document.write('<span style="white-space:nowrap;"><input type=\"checkbox\" class="select-choice" name=\"'+checkbox_name+'\" id=\"'+checkbox_name+'"><label for='+checkbox_name+'>'+Exercise.checkboxChoices[i][0]+'</label></input></span><br/>');
    }
}

function checkCheckboxChoices()
{
    var isCorrect;
    isCorrect = true;
    for(var i = 0; i < Exercise.checkboxChoices.length; i++){
        checkboxName = "selectAnswerCheckbox_"+i //Name of checkbox in DOM
        if(Exercise.checkboxChoices[i][1] != answerform[checkboxName].checked){
            isCorrect = false;
        }
    }
    handleCorrectness(isCorrect);
}

function array_sum(a) {

	var sum=0;
	for (var i=0; i<a.length; i++) {
		sum+=a[i];
	}
	return sum;
}

function appendQuestionHtml(html) {
    if (Exercise.fWriteToDoc)
        document.write(html);     
    else
        $("#question_content").append(html);
}

function appendAnswerHtml(html) {
    $("#answer_content").append(html)
}

function open_left_padding(pixels) {
    appendQuestionHtml("<div style=\'padding-left: " + pixels + "px\'>");
}

function close_left_padding() {
    appendQuestionHtml("</div>");
}

function write_step(text, step) //Deprecated
{
	appendQuestionHtml('<P><div class=\"step'+step+'\" style=\"position:relative; visibility:hidden;\"><font face=\"arial\" size=3>'+text+'</font></div></P>');
}

function write_step(text)
{
    appendQuestionHtml('<P><div class=\"step'+ Exercise.next_step_to_write + '\" style=\"position:relative; visibility:hidden;\"><font face=\"arial\" size=3>'+text+'</font></div></P>');
	Exercise.next_step_to_write++;
}

function write_table_step_generic(explanation, left, center, right)
{
	appendQuestionHtml(	'<tr class="step'+ Exercise.next_step_to_write + '" style="visibility:hidden;"><td align=left class=\"nobr\">'
        	+ '<div style=\"position:relative;\"><font face=\"arial\" size=4>' + '<FONT class=\"explanation\" class=\"nobr\">' + explanation + '</font>' +'</font></div>'
			+'</td><td align=right class=\"nobr\"><nobr>'
			+'<div style=\"position:relative;\"><font face=\"arial\" size=4>' + '`' + left + '`' + '</font></div>'
			+'</nobr></td><td align=left class=\"nobr\"><nobr>'
			+ '<div style=\"position:relative;\"><font face=\"arial\" size=4>' + '`'+ center + right + '`' + '</font></div>'
			+'</nobr></td></tr>');
			
	Exercise.next_step_to_write++;
}

function write_table_step(explanation, left, right)
{
    write_table_step_generic(explanation, left, '=', right);
}

function table_step_header(explanation, left, right)
{
    table_step_header_generic(explanation, left, '=', right);
}

function table_step_header_generic(explanation, left, center, right) 
{
    appendQuestionHtml('<center><table border=0><tr><td></td><td></td><td></td></tr><tr><td align=left class=\"nobr\"><font face=\"arial\" size=4>'+explanation+'</font></td><td align=right class=\"nobr\"><font face=\"arial\" size=4>`'+
			left+
			'</font></td><td align=left class=\"nobr\"><nobr><font face=\"arial\" size=4  class=\"nobr\">`' + center  +right+'`</font></nobr></td></tr>');
}

function table_step_footer()
{
	appendQuestionHtml('</table></center>');
}

function write_equation(equation)
{
	appendQuestionHtml('<p><font face=\"arial\" size=4><center>`'+equation+'`</center></font></p>');
}

function write_text(text)
{
	appendQuestionHtml('<p><font face=\"arial\" size=3>'+text+'</font></p>');
}

function equation_string(equation)
{
	return ('<p><font face=\"arial\" size=4><center>`'+equation+'`</center></font></p>');
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
		if ((Math.abs(n)%(i*i))==0)
			square_factor=i*i;
	}

	if (Math.abs(square_factor)==1) //the number is not factorable has the product of a perfect square and another number
	{
		return [n];
	}
	else
	{
		return [n/square_factor, square_factor];
	}
}

function reset_streak() {
    if ($("#hint_used").val() != 1) {
        fade_streaks();
        $.ajax({
            type: "POST",
            url: "/resetstreak",
            data: {	key: $("#key").val() },
            data_type: 'json'
        }); 
    }
    $("#hint_used").val("1");
}

function fade_streaks() {
    $(".unit-rating li.current-rating").animate({opacity: 0.0}, "fast");
    $(".unit-rating li.current-label").animate({opacity: 0.0}, "fast");
}

function get_reduced_fraction(numerator,denominator){
    var factorX = 1;
    var result={};
    //Find common factors of Numerator and Denominator
    for ( var x = 2; x <= Math.min( numerator, denominator ); x ++ ) {
        var check1 = numerator / x;
        if ( check1 == Math.round( check1 ) ) {
            var check2 = denominator / x;
            if ( check2 == Math.round( check2 ) ) {
                factorX = x;
            }
        }
    }

    result.numerator=(numerator/factorX);  //divide by highest common factor to reduce fraction then multiply by neg to make positive or negative
    result.denominator=denominator/factorX;  //divide by highest common factor to reduce fraction

    return result;
}

/*
* Access Level: Private
* Function: _rtrim
* Parameter1 Name: str
* Parameter1 Type: string
* Parameter1 Description: string to trim charector in
* Parameter2 Name: chars
* Parameter2 Type: String
* Parameter2 Description: char to br trimmed from string
*/
function rtrim(str, chars) {
    chars = chars || "\\s";
    return str.replace(new RegExp("[" + chars + "]+$", "g"), "");
}


/*
* Access Level: Private
* Function: _ltrim
* Parameter1 Name: str
* Parameter1 Type: string
* Parameter1 Description: string to trim charector in
* Parameter2 Name: chars
* Parameter2 Type: String
* Parameter2 Description: char to br trimmed from string
*/
function ltrim(str, chars) {
    chars = chars || "\\s" || "\\.";
    return str.replace(new RegExp("^[" + chars + "]+", "g"), "");
}

