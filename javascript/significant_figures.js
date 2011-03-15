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
    var _number = null;
    var _equation = null;
    var _hintStep = 0;
    var _stringNumberForHint = '';
    var _lHints = [
    'Digits from 1-9 are always significant.',
    'Zeros between two other significant digits are always significant',
    'Zeros to the right of the decimal place and another significant digit are significant',
    'Zeros used solely for spacing the decimal point are not significant',
    'Significant Numbers are: '
    ];

    //Private Methods

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
    var _rtrim = function (str, chars) {
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
    var _ltrim = function  (str, chars) {
        chars = chars || "\\s" || "\\.";
        return str.replace(new RegExp("^[" + chars + "]+", "g"), "");
    }

    /*
     * Access Level: Private
     * Function: _getSignificantNumbers
     * Parameter1 Name: pNumber
     * Parameter1 Type: float/integer
     * Parameter1 Description: Numbers to finr significant figure in
     */
    var _getSignificantNumbers = function(pNumber) {
        var lStringNumber = String(pNumber);

        if(lStringNumber.match(/^[0-9]+\.[0-9]+$/)) {
            lStringNumber = _ltrim(lStringNumber, '0.');
            _stringNumberForHint = lStringNumber;
            lStringNumber = lStringNumber.replace('.', '')
        } else {
            lStringNumber = _rtrim(lStringNumber, '0');
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
        var lNum1 = Math.abs(get_random());
        var lNum2 = Math.abs(get_random());
        var lStringifiedNumber = '';

        _number = lNum1/lNum2;

        lStringifiedNumber += _number
        lStringifiedNumber = lStringifiedNumber.substr(0, 5);

        _equation = 'Find the  Number of Significant Figures in: ' + lStringifiedNumber;
        _writeEquation("#dvQuestion", _equation, true); //Write New Equation        
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
     * Parameter1 Name: pSignificantNumbers
     * Parameter2 Name: pStringifiedNumber
     */
    var _createHints = function(pSignificantNumbers, pStringifiedNumber) {
        var lHint = 'Significant Numbers are: ';

        lHint += pStringifiedNumber.replace(pSignificantNumbers, '<span style="color: red;" >' + pSignificantNumbers + '</span>');
        _lHints[_lHints.length-1] = lHint;
    }


    /*
     * Access Level: Private
     * Function: _getHint
     * Parameter1 Name: pHintStep
     */
    var _getHint = function(pHintStep) {
        return (pHintStep < _lHints.length ? _lHints[pHintStep] : _lHints[_lHints.length-1]);
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
            $('#dvHint').html('<br /><span style="font-family: arial; font-size: 200%; font-weight: bold; color: gray; ">Hint: <center>' + _getHint(_hintStep++) + '</center></span>');
            steps_given++;
        }
    };
};

$(document).ready(function(){
    SignificantFigures.CountSignificantFigures.init();
});