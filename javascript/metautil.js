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
	var isCorrect = (parseFloat(document.getElementById("answer").value)==parseFloat(correctAnswer));
	// Attempt to register the correctness of the answer with the server, before telling the user 
	// whether it is correct.  This prevents the user from just reloading the page to quickly and quietly 
	// avoid blowing a streak when he gets a wrong answer.  If the attempt to register the correctness fails,
	// we don't worry about it because they might just be having connectivity problems or need to log in again.
	// That means it is still possible for a user to cheat (e.g. by logging out before clicking "Check Answer")
	// but it takes longer and is more noticeable.
	Http.get({ 
		method: Http.Method.Post,
		url: "/registercorrectness"
			+ "?key=" + document.getElementById("key").value
			+ "&correct=" + ((isCorrect && tries==0 && steps_given==0) ? 1 : 0),			
		callback: function() { }
		}, isCorrect);
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


/* 
	XmlHttpRequest Wrapper
	Version 1.2.2
	29 Jul 2005 
	adamv.com/dev/
*/

var Http = {
	ReadyState: {
		Uninitialized: 0,
		Loading: 1,
		Loaded:2,
		Interactive:3,
		Complete: 4
	},
		
	Status: {
		OK: 200,
		
		Created: 201,
		Accepted: 202,
		NoContent: 204,
		
		BadRequest: 400,
		Forbidden: 403,
		NotFound: 404,
		Gone: 410,
		
		ServerError: 500
	},
		
	Cache: {
		Get: 1,
		GetCache: 2,
		GetNoCache: 3,
		FromCache: 4
	},
	
	Method: {Get: "GET", Post: "POST", Put: "PUT", Delete: "DELETE"},
	
	enabled: false,
	logging: false,
	_get: null,	// Reference to the XmlHttpRequest object
	_cache: new Object(),
	
	Init: function(){
		Http._get = Http._getXmlHttp()
		Http.enabled = (Http._get != null)
		Http.logging = (window.Logging != null);
	},
	
	_getXmlHttp: function(){
	/*@cc_on @*//*@if (@_jscript_version >= 5)
		try { return new ActiveXObject("Msxml2.XMLHTTP"); } 
		catch (e) {} 
		try { return new ActiveXObject("Microsoft.XMLHTTP"); } 
		catch (e) {} 
	@end @*/
		try { return new XMLHttpRequest();}
		catch (e) {}

		return null;
	},

/*
	Params:
		url: The URL to request. Required.
		cache: Cache control. Defaults to Cache.Get.
		callback: onreadystatechange function, called when request is completed. Optional.
		method: HTTP method. Defaults to Method.Get.
*/
	get: function(params, callback_args){	
		if (!Http.enabled) throw "Http: XmlHttpRequest not available.";
		
		var url = params.url;
		if (!url) throw "Http: A URL must be specified";
				
		var cache = params.cache || Http.Cache.Get;
		var method = params.method || Http.Method.Get;
		var callback = params.callback;
		
		if ((cache == Http.Cache.FromCache) || (cache == Http.Cache.GetCache))
		{
			var in_cache = Http.from_cache(url, callback, callback_args)

			if (Http.logging){
				Logging.log(["Http: URL in cache: " + in_cache]);
			}

			if (in_cache || (cache == Http.Cache.FromCache)) return in_cache;
		}
		
		if (cache == Http.Cache.GetNoCache)
		{
			var sep = (-1 < url.indexOf("?")) ? "&" : "?"	
			url = url + sep + "__=" + encodeURIComponent((new Date()).getTime());
		}
	
		// Only one request at a time, please
		if ((Http._get.readyState != Http.ReadyState.Uninitialized) && 
			(Http._get.readyState != Http.ReadyState.Complete)){
			this._get.abort();
			
			if (Http.logging){
				Logging.log(["Http: Aborted request in progress."]);
			}
		}
		
		Http._get.open(method, url, true);

		Http._get.onreadystatechange =  function() {
			if (Http._get.readyState != Http.ReadyState.Complete) return;
			
			if (Http.logging){
				Logging.log(["Http: Returned, status: " + Http._get.status]);
			}

			if ((cache == Http.Cache.GetCache) && (Http._get.status == Http.Status.OK)){
				Http._cache[url] = Http._get.responseText;
			}
			
			if (callback_args == null) callback_args = new Array();

			var cb_params = new Array();
			cb_params.push(Http._get);
			for(var i=0;i<callback_args.length;i++)
				cb_params.push(callback_args[i]);
				
			callback.apply(null, cb_params);
		}
		
		if(Http.logging){
			Logging.log(["Http: Started\n\tURL: " + url + "\n\tMethod: " + method + "; Cache: " + Hash.keyName(Http.Cache,cache)])
		}
		
		Http._get.send(params.body || null);
	},
	
	from_cache: function(url, callback, callback_args){
		var result = Http._cache[url];
		
		if (result != null) {
			var response = new Http.CachedResponse(result)
			
			var cb_params = new Array();
			cb_params.push(response);
			for(var i=0;i<callback_args.length;i++)
				cb_params.push(callback_args[i]);
							
			callback.apply(null, cb_params);
				
			return true
		}
		else
			return false
	},
	
	clear_cache: function(){
		Http._cache = new Object();
	},
	
	is_cached: function(url){
		return Http._cache[url]!=null;
	},
	
	CachedResponse: function(response) {
		this.readyState = Http.ReadyState.Complete
		this.status = Http.Status.OK
		this.responseText = response
	}	
}

Http.Init()

function json_response(response){
	var js = response.responseText;
	try{
		return eval(js); 
	} catch(e){
		if (Http.logging){
			Logging.logError(["json_response: " + e]);
		}
		else{
			alert("Error: " + e + "\n" + js);
		}
		return null;
	}
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

