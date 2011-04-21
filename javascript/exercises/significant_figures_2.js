/*
* Author: Ali Muzaffar
* Date: 16 March 2011
* Description: Significant Figures Multiplication.
*/

//namespace: NewSignificantFigures
NewSignificantFigures= function(){}

//class: MultiplySignificantFigures
NewSignificantFigures.MultiplySignificantFigures = new function(){
    var _number = null;
    var _number2 = null;
    var _equation = null;
    var _hintStep = 0;

    /*
     * Access Level: Private
     * Function: _getSignificantNumbers
     * Parameter1 Name: Number
     * Parameter1 Type: float/integer
     * Parameter1 Description: Numbers to find significant figure in
     */
    var _getSignificantNumbers = function(Number) {
        //console.log("the raw number is "+pNumber);
        var lStringNumber = String(Number);
        var numberInfo= {};
		
        if(lStringNumber.match(/^[0-9]+\.[0-9]+$/)) {
            lStringNumber = ltrim(lStringNumber, '0.');
            numberInfo.decimal=1;
            lStringNumber = lStringNumber.replace('.', '');
        } else {
            lStringNumber = rtrim(lStringNumber, '0');
            numberInfo.decimal=0;
        }
        numberInfo.basic=String(Number);
        numberInfo.stripped=lStringNumber;
        numberInfo.sigCount=lStringNumber.length;        
        return numberInfo;
    }
	
	
    /*
     * Access Level: Private
     * Function: _createNumber
     * Description: Function is used to create random significiant number
     * Parameter: none
     */
    var _createNumber = function(){
        var lStringifiedNumber = '';
        var lStringifiedNumber2 = '';
        var _answer=null;
        var  simplifiedAnswer;
        //step 1
        _number = (Math.abs(get_random()))/(Math.abs(get_random()));
        
        _number2=(Math.abs(get_random()))/(Math.abs(get_random()));
        lStringifiedNumber += _number;
        lStringifiedNumber2+=_number2;
        
        //step2
        lStringifiedNumber = lStringifiedNumber.substr(0, 5);
        lStringifiedNumber2 = lStringifiedNumber2.substr(0, 5);
		
        //step3
        _answer=_getSignificantNumbers(lStringifiedNumber*lStringifiedNumber2);
				
        //step4
        var significantCount1=_getSignificantNumbers(lStringifiedNumber);
        var significantCount2=_getSignificantNumbers(lStringifiedNumber2);
		
        if(significantCount1.sigCount>=significantCount2.sigCount){
            simplifiedAnswer=displaySigFigs(
                _answer.basic,
                significantCount2.sigCount,
                -999,
                false
                );
        } else {
            simplifiedAnswer=displaySigFigs(
                _answer.basic,
                significantCount1.sigCount,
                -999,
                false
                );
        }
		
        _answer.rounded=simplifiedAnswer;
        _equation = '<p style="font-size:85%;">When considering significant figures, <font face="arial" size=5>`' + lStringifiedNumber+'` `\\times` `' + lStringifiedNumber2 + '` `=` `?`</font></p>';
        _writeEquation("#dvQuestion", _equation, false); //Write New Equation      
        setCorrectAnswer(simplifiedAnswer);
        _makeHints(significantCount1, significantCount2,_answer);

    }


    /*
     * Function:_writeEquation
     * Access Level: Private
     *
     * Parameters1 Name: Selector
     * Parameters1 Type: String
     * Parameters1 Detail: String Contain The Jquery Selector Of Div where expression need to be displayed.
     *
     * Parameters2 Name: Equation
     * Parameters2 Type: String
     * Parameters2 Detail: Expression that need to be displayed.
     *
     * Parameters3 Name: Equation
     * Parameters3 Type: String
     * Parameters3 Detail: To check if expression should be centered aligned.
     *
     * Description:Formats and generates the question to be asked.
     */
    var _writeEquation = function(Selector,Equation, IsCentered){
        if(IsCentered){
            $(Selector).append('<center><span style="font-family: arial; font-size: 200%; font-weight: bold;">' + Equation + '</span></center>');
        } else {
            $(Selector).append('<span style="font-family: arial; font-size: 200%; font-weight: bold;">' + Equation + '</span>');
        }
    }


    /*
     * Access Level: Private
     * Function: _makeHints
     * Parameter1 Name: Number1
     * Parameters1 Type: Object
     * Parameters1 Detail: This object contains information about the first number that was generated
     *
     * Parameter2 Name: Number2
     * Parameters2 Type: Object
     * Parameters2 Detail: This object contains information about the second number that was generated
     * 
     * Parameter3 name: Answer
     * Parameters1 Type: Object
     * Parameters1 Detail: This object contains information about the answer
     *
     * Description: Generates the hints for the problem
     */
    var _makeHints = function(Number1,Number2,Answer) {
        var str="";
        var answerSigCount= (Number1.sigCount<=Number2.sigCount)?Number1:Number2;
        str +="<div id='hint0' style='display:none; font-size: 150%; font-weight: bold;color:#999;'><br/>When multiplying with significant figures, the answer can't have more significant digits than either of the terms being multiplied.</div>";
        str +="<div id='hint1' style='display:none; font-size: 150%; font-weight: bold;color:#999;'><br/>First, figure out which term has the fewest significant figures.</div>";
        str +="<div id='hint2' style='display:none; font-size: 150%; font-weight: bold;color:#999;'><br/>In this case, " + Number1.basic + " has " + Number1.sigCount + " significant figure(s), and " + Number2.basic + " has " + Number2.sigCount + " significant figure(s).</div>";
        if(Number1.sigCount == Number2.sigCount){
            str +="<div id='hint3' style='display:none; font-size: 150%; font-weight: bold;color:#999;'><br/>Since both the terms " + Number1.basic + " and " + Number2.basic + " have the same number of (" + Number2.sigCount + ") significant digit(s), we will round our answer to " + Number2.sigCount + " significant digit(s).</div>";
        } else {
            str +="<div id='hint3' style='display:none; font-size: 150%; font-weight: bold;color:#999;'><br/>Since " + answerSigCount.basic + " has only " + answerSigCount.sigCount + " significant digit(s), we will round our answer to " + answerSigCount.sigCount + " significant digit(s).</div>";
        }
        str +=  '<div id="hint4" style="display:none;font-family: arial; font-size: 150%; font-weight: bold;color:#999;"><br/><p style="font-size:85%;"><font face="arial" size=5>`' + Number1.basic +'` `\\times` `' + Number2.basic + '` `=` `' + (Number1.basic*Number2.basic) + '`</font></p></div>';

        //str += "<div id='hint4' style='display:none;font-family: arial; font-size: 150%; font-weight: bold;color:#999;'><br/>" + Number1.basic + " * " + Number2.basic + " = " + (Number1.basic*Number2.basic) + ".</div>";
        str += "<div id='hint5' style='display:none; font-size: 150%; font-weight: bold;color:#999;'><br/>" + (Number1.basic*Number2.basic) + " rounded to " + answerSigCount.sigCount + " significant digit(s) is <span style='color:" + getNextColor() + ";'>" + Answer.rounded + "</span>.</div>";
        $('#dvHint').html(str);
    }    
    return {        
        /*
         * Access Level: Public
         * Function: init
         */
        init: function(){
            _createNumber();
        },


        /*
         * Access Level: Public
         * Function: next_step
         * Description: Function used to generate next step of Hint.
         */
        next_step: function (){
            if(_hintStep <= 5){
                $('#hint'+_hintStep).css('display','block');
                _hintStep++;
            }
            steps_given++;
        }
    };
};


$(document).ready(function(){
    NewSignificantFigures.MultiplySignificantFigures.init();
})