/*
* Author: Ali Muzaffar
* Date: 11 March 2011
* Description: Significant Figures.
*/

//namespace: SignificantFigures
SignificantFigures= function(){}


//class: CountSignificantFigures
SignificantFigures.CountSignificantFigures = new function(){
    //Private Members
    var _equation = null;
    var _hintStep = 0;
    var _stringNumberForHint = '';
    var _combinations=[
    "----",
    "---",
    "--",
    "-",
    "0.00-",
    "-.-",
    "-.--",
    "-.---",
    "0.0-",
    "-.-",
    "0.000-",
    "-.----",
    "--.-",
    "--.--",
    "0.--",
    "--.---",
    "---.-",
    "---.--",
    "---.---",
    "---.----",
    "----.----"];
    var _lHints = [
    'Digits from 1-9 are always significant.',
    'Zeros between two other significant digits are always significant',
    'Zeros to the right of the decimal place and another significant digit are significant',
    'Zeros used solely for spacing the decimal point are not significant',
    'The significant numbers are: ',
    '....So there are' 
    ];

    //Private Methods
    
    /*
     * Function:_randOrder
     * Access Level: Private
     * Parameters: none
     * Description:Function used to set radom sort order of an array.
     */
    var _randOrder = function (){
        return (Math.round(Math.random())-0.5);
    }


    /*
     * Access Level: Private
     * Function: _getSignificantNumbers
     * Parameter1 Name: Number
     * Parameter1 Type: float/integer
     * Parameter1 Description: Numbers to finr significant figure in
     */
    var _getSignificantNumbers = function(Number) {
        var lStringNumber = String(Number);
        lStringNumber = lStringNumber.replace('-', '');
        if(lStringNumber.match(/^[0-9]+\.[0-9]+$/)) {
            lStringNumber = ltrim(lStringNumber, '0.');
            _stringNumberForHint = lStringNumber;
            lStringNumber = lStringNumber.replace('.', '')
        } else {
            lStringNumber = rtrim(lStringNumber, '0');
            lStringNumber = ltrim(lStringNumber, '0');
            _stringNumberForHint = lStringNumber;
        }

        return lStringNumber.length;
    }

    /*
     * Access Level: Private
     * Function: _createNumber
     * Parameter: none
     */
    var _createNumber = function(){
        var lStringifiedNumber = '';
        _combinations.sort( _randOrder );
        var combination = _combinations[getRandomIntRange(0,12)];
        for(var i=0; i<combination.length; i++){
            if(combination.substring(i,i+1)=="-"){
                lStringifiedNumber += (getRandomIntRange(0,9)).toString();
            } else {
                lStringifiedNumber += combination.substring(i,i+1);
            }
        }
        if(getRandomIntRange(0,8) > 5){
            lStringifiedNumber = "-" + lStringifiedNumber;
        }
        _equation = 'Find the  number of significant figures in: ' + lStringifiedNumber;
        _writeEquation("#dvQuestion", _equation, false); //Write New Equation        
        setCorrectAnswer(_getSignificantNumbers(lStringifiedNumber));
        _createHints(_stringNumberForHint, lStringifiedNumber);
    }


    /*
     * Access Level: Private
     * Function: _createNumber
     * Parameter: none
     */
    var _writeEquation = function(pSelector,pEquation, pIsCentered){
        if(pIsCentered){
            $(pSelector).append('<center><span style="font-family: arial; font-size: 200%; font-weight: bold;">'+pEquation+'</span></center>');
        } else {
            $(pSelector).append('<span style="font-family: arial; font-size: 200%; font-weight: bold;">'+pEquation+'</span>');
        }
    }


    /*
     * Access Level: Private
     * Function: _createHints
     * Parameter1 Name: SignificantNumbers
     * Parameter2 Name: StringifiedNumber
     */
    var _createHints = function(SignificantNumbers, StringifiedNumber) {
        var lHint = 'Significant Numbers are: ';
        var str='';
        lHint += StringifiedNumber.replace(SignificantNumbers, '<span style="color: red;" >' + SignificantNumbers + '</span>');
        _lHints[_lHints.length-2] = lHint;
        _lHints[_lHints.length-1] =  (SignificantNumbers.indexOf('.')!=-1)?'....So there are '+ (SignificantNumbers.length-1) +' significant figures':'....So there are '+ (SignificantNumbers.length) +' significant figures';
        
        str+="<div id='hint0' style='display:none;font-family: arial; font-size: 150%; font-weight: bold;color:#999; ' ><br/>"+ _lHints[0]+"</div>";
        str+="<div id='hint1' style='display:none;font-family: arial; font-size: 150%; font-weight: bold;color:#999;' ><br/>"+ _lHints[1]+"</div>";
        str+="<div id='hint2' style='display:none;font-family: arial; font-size: 150%; font-weight: bold;color:#999;' ><br/>"+ _lHints[2]+"</div>";
        str+="<div id='hint3' style='display:none;font-family: arial; font-size: 150%; font-weight: bold;color:#999;' ><br/>"+ _lHints[3]+"</div>";
        str+="<div id='hint4' style='display:none;font-family: arial; font-size: 150%; font-weight: bold;color:#999;' ><br/>"+ _lHints[4]+"</div>";
        str+="<div id='hint5' style='display:none;font-family: arial; font-size: 150%; font-weight: bold;color:#999;' ><br/>"+ _lHints[5]+"</div>";        
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
         * Function: init
         */
        next_step: function (){
            if(_hintStep<=5){ 
                $('#hint'+_hintStep).css('display','block');
                _hintStep++;
            }
            steps_given++;
        }
    };
};

$(document).ready(function(){
    SignificantFigures.CountSignificantFigures.init();
});