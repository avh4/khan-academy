/***
This part handles names and grammar for wordproblems
**/

//Declare the variables
var C = null;
var B = null;
var A = null;
var correctAnswer = null; 
var boys = ["Arman", "Salman", "Ali", "Jonathan", "Tarush", "Zack", "Omar"];
var girls = ["Umaima", "Nadia", "Anuranjita", "Nazrat", "Rabab", "Chutney", "Gulnar", "Naseem"];
var person1 = null;
var person2 = null;
var pronoun1 = "he";
var pronoun2 = "he";


if (KhanAcademy.random()>KhanAcademy.random())
{
	person1 = boys.splice(getRandomIntRange(0,boys.length-1),1);
}
else
{
	person1 = girls.splice(getRandomIntRange(0,girls.length-1),1);
	pronoun1 = "she";
}
	
if (KhanAcademy.random()>KhanAcademy.random())
{
	person2 = boys.splice(getRandomIntRange(0,boys.length-1),1);
}
else
{
	person2 = girls.splice(getRandomIntRange(0,girls.length-1),1);
	pronoun2 = "she";
}

function commaFormat(n)
{
	var dec = Math.round((n-Math.floor(n))*1000)/1000;
	var decString = "";
	if (dec > 0)
	{
		decString+=dec;
		decString=decString.substring(1, decString.length);
	}
	
	if(n>999)
		return (formatNumber(Math.floor(n))+decString);
	else
		return n;
}


function formatNumber(n)
{
	var nString =""+n;

	if(nString.length>3)
	{
		return (formatNumber(nString.substr(0,nString.length-3))+","+nString.substr(nString.length-3,3));
	}
	else
	{
		return nString;
	}
}

function fraction(n,d)
{
	var expressionString = "<table border=0 cellpadding=0 cellspacing=0><tr><td align=center>"+n+
		"</td></tr><tr><td width=10px height=1px bgcolor=#000000 cellpadding=0 cellspacing=0><img width=1 height=1 alt=\"\"></td></tr><tr><td  align=center>"+d+
		"</td></tr></table>";
		
	return expressionString;
}

