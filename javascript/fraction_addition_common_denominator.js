/*
* Author: Gohar-UL-Islam
* Date: 20 Feb 2011
* Description: Fraction addition exercise with common dinominators.
*/


/*
 * Fraction Addition Namespace
 */
FractionAddition= function(){}

/*
 * Class Name: AdditionWithCommonDenominator
 */
FractionAddition.AdditionWithCommonDenominator = new function(){

    /*Private Members*/
    var _hintsGiven = 0;
    var _num1 = null;
    var _num2 = null;
    var _den1 = null;
    var _den2 = null;
    var _commonDenominator;
    var _equation = null;
    var _raphaelHandle = Raphael('holder',700,400);

    /*Private Methods*/

    /*
     * Function:_createEqationWithCommonDenominator
     * Access Level: Private
     * Parameters: none
     * Description:Creates a fraction addition equation with common dinominators
     */
    var _createEqationWithCommonDenominator = function(){
        _num1 = Math.abs(get_random());
        _num2 = Math.abs(get_random());
        if(_num1 < _num2){
            _den1 = get_randomInRange(_num2,_num2 + 10,0);
        } else {
            _den1 = get_randomInRange(_num1,_num1 + 10,0);
        }
        _den2 = _den1;
        _commonDenominator = getLCM(_den1, _den2);//Get LCM Of Denominators
        _equation = "`"+ _num1 + "/" + _den1 + "` `+` `" + _num2 + "/" + _den2 + "`";

        _writeEquation("#dvQuestion", _equation, true);//Write New Equation
        setCorrectAnswer((_num1*_commonDenominator/_den1)+(_num2*_commonDenominator/_den2) + "/" + _commonDenominator);
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
     * Description:Creates a fraction subtraction equation.
     */
    var _writeEquation = function(pSelector,pEquation, pIsCentered){
        if(pIsCentered){
            $(pSelector).append('<p><font face=\"arial\" size=4><center>'+pEquation+'</center></font></p>');
        } else {
            $(pSelector).append('<p><font face=\"arial\" size=4>'+pEquation+'</font></p>');
        }
    }


    /*
     * Access Level: Private
     * Function: _createWrongChoices
     * Parameters: none
     * Detail: Create wrong choices for multiple options
     */
    var _createWrongChoices = function (){
        addWrongChoice(format_fraction(_num1 + _num2 ,_den1 + _den2));
        addWrongChoice(format_fraction(_num1 + _num2, _commonDenominator));
        addWrongChoice(format_fraction(_num1 - _num2, _commonDenominator));
        var wrong_den = (_num1*_commonDenominator/_den1)+(_num2*_commonDenominator/_den2);
        if (wrong_den != 0)
            addWrongChoice(format_fraction(_commonDenominator, wrong_den));
        addWrongChoice(format_fraction(-1*(_num1*_commonDenominator/_den1)+(_num2*_commonDenominator/_den2),_commonDenominator));
        addWrongChoice(format_fraction(_num1*_num2,_den2*_den1));
        addWrongChoice(format_fraction((_num1*_commonDenominator/_den1)-(_num2*_commonDenominator/_den2),_commonDenominator));
    }


    /*
     * Access Level: Private
     * Function: _createAnswers
     * Parameters: none
     * Detail: Display answer options on screen
     */
    var _createAnswers = function(){
        var availAnswers = 1 + possibleAnswers.length + definiteWrongAnswers.length; // only so many answers available
        answerChoices = new Array(Math.min(availAnswers, 5)); // at most 5 answers displayed, resize to fit
        correctchoice = Math.round(KhanAcademy.random()*(answerChoices.length-0.02)-.49);
        var possibleWrongIndices = randomIndices(possibleAnswers.length);
        var definiteWrongIndices = randomIndices(definiteWrongAnswers.length);
        for (var i=0; i<answerChoices.length; i++) {
            if (i==correctchoice){
                answerChoices[i]='`'+correct_answer+'`';
            } else {
                if (definiteWrongIndices.length>0){
                    answerChoices[i] = '`' + definiteWrongAnswers[definiteWrongIndices.pop()]+'`';
                } else if (possibleWrongIndices.length>0) {
                    answerChoices[i] = '`' + possibleAnswers[possibleWrongIndices.pop()]+'`';
                }
            }
        }        
        // if you need to rearrange order or answers implement preDisplay function in derived html
        if (window.preDisplay){
            preDisplay(answerChoices, correctchoice);
        }
        for (i=0; i<answerChoices.length; i++){
            _writeEquation("#dvAnswers",'<span style="white-space:nowrap;"><input type=\"radio\" class="select-choice" name=\"selectAnswer\" onClick=\"select_choice('+i+')\">' + answerChoices[i] + '</input></span><br/>', false);
        }
    }


    /*
     * Access Level: Private
     * Function: _createHint
     * Parameter1 Name: pMyShare
     * Parameters1 Type: integer
     * Parameters1 Detail: This is the value of the neumirator
     *
     * Parameter2 Name: pMyTotal
     * Parameters2 Type: integer
     * Parameters2 Detail: This is the value of denominator
     *
     * Parameter3 name: pX
     * Parameters3 Type: integer
     * Parameters3 Detail: X-co-ordinate for the center of Pie Chart
     *
     * Parameter4 name: pY
     * Parameters4 Type: integer
     * Parameters4 Detail: Y-co-ordinate for the center of Pie Chart
     *
     * Parameter4 name: pRadius
     * Parameters4 Type: integer
     * Parameters4 Detail: Radius for the pie chart
     *
     * Description: Draws the pie charts with raphael.
     */
    var _createHint =function(pMyShare, pMyTotal, pX,pY, pRadius) {
        var pieData=new Array();
        var colors=new Array();
        for (var i = 0; i < pMyTotal; i++){
            if (i < pMyShare) {
                if (i % 2) {
                    colors[i] = "#C8F526";
                    pieData[i]=1;
                } else {
                    colors[i] = "#BCE937";
                    pieData[i]=1;
                }
            } else {
                if (i % 2){
                    colors[i] = "#FFE303";
                    pieData[i]=1;
                } else {
                    pieData[i]=1;
                    colors[i] = "#FBEC5D";
                }
            }                      
        }                     
        var opts={};
        opts.stroke="#ffffff";
        opts.strokewidth=1;
        opts.colors=colors;
        _raphaelHandle.g.piechart(pX, pY, pRadius, pieData,opts);
    }
    return {
        /*Public Methods*/


        /*
        * Access Level: Public
        * Function: init
        * Parameters: none
        * Detail: Initialize Fraction Addition Exercise
        */
        init: function(){
            _createEqationWithCommonDenominator();
            _createWrongChoices();
            _createAnswers();
        },


        /*
        * Access Level: Private
        * Function: next_step
        * Parameters: none
        * Detail: Create next step for user.
        */
        next_step: function (){
            if (_hintsGiven==0){
                _createHint(_num1, _den1, 105, 95, 90,'holder');
            } else if (_hintsGiven==1) {
                _createHint(_num2, _den2,  320,95,  90,'holder');
            }
            _hintsGiven++;
            steps_given++;
        }
    };
};

$(document).ready(function(){
    FractionAddition.AdditionWithCommonDenominator.init();
})