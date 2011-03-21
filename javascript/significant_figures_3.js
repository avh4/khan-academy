/*
* Author: Ali Muzaffar
* Date: 15 March 2011
* Description: Significant Figures Division.
*/

//namespace: NewSignificantFigures
NewSignificantFigures= function(){}

//class: DivideSignificantFigures
NewSignificantFigures.DivideSignificantFigures = new function(){
    //Private Members
    var _number = null;
    var _number2 = null;
    var _equation = null;
    var _hintStep = 0;
    var _combinations=[
    "----",
    "---",
    "--",
    "-",
    "-.-",
    "-.--",
    "-.---",
    "--.-",
    "--.--",
    "--.---",
    "---.-",
    "---.--",
    "---.---"];

    //Private Methods


    /*
     * Access Level: Private
     * Function: _rtrim
     * Parameter1 Name: str
     * Parameter1 Type: string
     * Parameter1 Description: string to trim character in
     * Parameter2 Name: chars
     * Parameter2 Type: String
     * Parameter2 Description: char to br trimmed from string
     */
    var _rtrim = function (str, chars) {
        chars = chars || "\\s";
        return str.replace(new RegExp("[" + chars + "]+$", "g"), "");
    }


    /*
     * Access Level: Private
     * Function: _ltrim
     * Parameter1 Name: str
     * Parameter1 Type: string
     * Parameter1 Description: string to trim character in
     * Parameter2 Name: chars
     * Parameter2 Type: String
     * Parameter2 Description: char to br trimmed from string
     */
    var _ltrim = function  (str, chars) {
        chars = chars || "\\s" || "\\.";
        return str.replace(new RegExp("^[" + chars + "]+", "g"), "");
    }


    /*
     * Access Level: Private
     * Function: _getSignificantNumbers
     * Parameter1 Name: pNumber
     * Parameter1 Type: float/integer
     * Parameter1 Description: Numbers to find significant figure in
     */
    var _getSignificantNumbers = function(pNumber){
        var lStringNumber = String(pNumber);		
        var numberInfo= {};
		
        if(lStringNumber.match(/^[0-9]+\.[0-9]+$/)){
            lStringNumber = _ltrim(lStringNumber, '0.');			
            numberInfo.decimal=1;
            lStringNumber = lStringNumber.replace('.', '')
        } else {
            lStringNumber = _rtrim(lStringNumber, '0');
            numberInfo.decimal=0;
        }
        numberInfo.basic=String(pNumber);
        numberInfo.stripped=lStringNumber;
        numberInfo.sigCount=lStringNumber.length;
        
        return numberInfo;
    }
		

    /*
     * Access Level: Private
     * Function: _createNumber
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
    
        while(_number==0 || _number=='Infinity'){
            _number = (Math.abs(get_random()))/(Math.abs(get_random()));;
        }
        
        while(_number2==0 || _number2=='Infinity'){
            _number2 = (Math.abs(get_random()))/(Math.abs(get_random()));;
        }
        lStringifiedNumber += _number;
        lStringifiedNumber2+=_number2;
        
        //step2
        lStringifiedNumber = lStringifiedNumber.substr(0, 5);
        lStringifiedNumber2 = lStringifiedNumber2.substr(0, 5);
		
        //step3
        _answer=_getSignificantNumbers(lStringifiedNumber/lStringifiedNumber2);		
		
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
        _equation = 'When considering significant figures, ' + lStringifiedNumber+' / '+lStringifiedNumber2+' = ?';
        _writeEquation("#dvQuestion", _equation, false); //Write New Equation       
        setCorrectAnswer(simplifiedAnswer);
        _makeHints(significantCount1, significantCount2,_answer);

    }


    /*
     * Function:_writeEquation
     * Access Level: Private
     *
     * Parameters1 Name: pSelector
     * Parameters1 Type: String
     * Parameters1 Detail: String Contain The Jquery Selector Of Div where expression need to be displayed.
     *
     * Parameters2 Name: pEquation
     * Parameters2 Type: String
     * Parameters2 Detail: Expression that need to be displayed.
     *
     * Parameters3 Name: pEquation
     * Parameters3 Type: String
     * Parameters3 Detail: To check if expression should be centered aligned.
     *
     * Description:Formats and generates the question.
     */
    var _writeEquation = function(pSelector,pEquation, pIsCentered){
        if(pIsCentered){
            $(pSelector).append('<center><span style="font-family: arial; font-size: 200%; font-weight: bold;">' + pEquation + '</span></center>');
        } else {
            $(pSelector).append('<span style="font-family: arial; font-size: 200%; font-weight: bold;">' + pEquation + '</span>');
        }
    }


    /*
     * Access Level: Private
     * Function: _makeHints
     * Parameter1 Name: pNumber1
     * Parameters1 Type: Object
     * Parameters1 Detail: This object contains information about the first number that was generated
     *
     * Parameter2 Name: pNumber2
     * Parameters2 Type: Object
     * Parameters2 Detail: This object contains information about the second number that was generated
     *
     * Parameter3 name: pAnswer
     * Parameters1 Type: Object
     * Parameters1 Detail: This object contains information about the answer
     *
     * Description: Generates the hints for the problem
     */
    var _makeHints = function(pNumber1,pNumber2,pAnswer) {
        var str="";
       var answerSigCount= (pNumber1.sigCount<=pNumber2.sigCount)?pNumber1:pNumber2;       
        str+="<div id='hint0' style='display:none;font-family: arial; font-size: 150%; font-weight: bold;color:#999;' ><br/>When quantities are multiplied or divided, the number of significant figures in the answer is equal to the number of significant figures in the quantity with the smallest number of significant figures.</div>";
        str+="<div id='hint1' style='display:none;font-family: arial; font-size: 150%; font-weight: bold;color:#999;' ><br/>Determine which number has smaller significant count between <span style='color:red'>"+pNumber1.basic+"</span> and <span style='color:red'>"+pNumber2.basic+"</span></div>";
        str+="<div id='hint2' style='display:none;font-family: arial; font-size: 150%; font-weight: bold;color:#999;'><br/>"+pNumber1.basic+" / "+pNumber2.basic+" = "+(pNumber1.basic/pNumber2.basic)+"</div>";
        str+="<div id='hint3' style='display:none;font-family: arial; font-size: 150%; font-weight: bold;color:#999;'><br/>Now round the division result to "+answerSigCount.sigCount+" significant digit(s) as "+answerSigCount.basic+" has a minimum number of significant digit(s) that is "+answerSigCount.sigCount+"</div>";
        str+="<div id='hint4' style='display:none;font-family: arial; font-size: 150%; font-weight: bold;color:#f00'><br/>The Answer is "+pAnswer.rounded+" </div>";
        $('#dvHint').html(str);
    }    
    return {

        /*
         * Access Level: Public
         * Function: init
         * Description: initialize exercise
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
            if(_hintStep <= 4){
                $('#hint'+_hintStep).css('display','block');
                _hintStep++;
            }
            steps_given++;
        }
    };
};

$(document).ready(function(){
    NewSignificantFigures.DivideSignificantFigures.init();
})