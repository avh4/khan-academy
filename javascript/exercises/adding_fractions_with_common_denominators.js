/*
 * Author: Gohar-UL-Islam
 * Date: 20 Feb 2011
 * Description: Fraction addition exercise with common dinominators.
 */


/*
 * Fraction Addition Namespace
 */
FractionAddition = function(){}

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
    var _myColor=getNextColor() ;
    var _totalColor= "#ccc" ;
    var _raphaelHandle = Raphael('holder',500,200);
    var _reducedNominator;
    var _reducedDenominator;
    var _unreducedNominator;

    /*Private Methods*/

    /*
     * Function:_createEqationWithCommonDenominator
     * Access Level: Private
     * Parameters: none
     * Description:Creates a fraction addition equation with common dinominators
     */
    var _createEquationWithCommonDenominator = function(){
        var temp;
        _num1 = Math.abs(get_random());
        _num2 = Math.abs(get_random());
        
        var max = Math.max(_num1, _num2);
        _den1 = getRandomIntRange(max, max + 10);
        _den2 = _den1;
        _commonDenominator = _den1;
        _equation = "`"+ _num1 + "/" + _den1 + "` `+` `" + _num2 + "/" + _den2 + "`";
        $("#dvHintText2").append('`?/' + _den1 + '`');
        $("#dvHintText4").append(_equation + " &nbsp;&nbsp;`=` &nbsp;&nbsp;`" 
                            + "(" + _num1 + " + " + _num2 + ") / " + _den1  
                            + "="+ ((_num1*_commonDenominator/_den1)+(_num2*_commonDenominator/_den2)) + "/" + _commonDenominator + "`");
        _writeEquation("#dvQuestion", _equation +  " `=` ?", true);//Write New Equation
        _unreducedNominator=(_num1*_commonDenominator/_den1)+(_num2*_commonDenominator/_den2);
        temp=get_reduced_fraction(_unreducedNominator,_commonDenominator);
        _reducedNominator=temp.numerator;
        _reducedDenominator=temp.denominator;
        setCorrectAnswer(temp.numerator + "/" + temp.denominator);
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
     * Description:Creates a fraction subtraction equation.
     */
    var _writeEquation = function(Selector,Equation, IsCentered){
        if(IsCentered){
            $(Selector).append('<p><font face=\"arial\" size=4><center>'+Equation+'</center></font></p>');
        } else {
            $(Selector).append('<p><font face=\"arial\" size=4>'+Equation+'</font></p>');
        }
    }
   

    /*
     * Access Level: Private
     * Function: _createHint
     * Parameter1 Name: MyShare
     * Parameters1 Type: integer
     * Parameters1 Detail: This is the value of the neumirator
     *
     * Parameter2 Name: MyTotal
     * Parameters2 Type: integer
     * Parameters2 Detail: This is the value of denominator
     *
     * Parameter3 name: X
     * Parameters3 Type: integer
     * Parameters3 Detail: X-co-ordinate for the center of Pie Chart
     *
     * Parameter4 name: Y
     * Parameters4 Type: integer
     * Parameters4 Detail: Y-co-ordinate for the center of Pie Chart
     *
     * Parameter4 name: Radius
     * Parameters4 Type: integer
     * Parameters4 Detail: Radius for the pie chart
     *
     * Description: Draws the pie charts with raphael.
     */
    var _createHint =function(MyShare, MyTotal, X,Y, Radius) {
        var pieData=new Array();
        var colors=new Array();       
        for (var i = 0; i < MyTotal; i++){
            if (i < MyShare) {
                if (i % 2) {
                    colors[i] = _myColor;
                    pieData[i]=1;
                } else {
                    colors[i] = _myColor;
                    pieData[i]=1;
                }
            } else {
                if (i % 2){
                    colors[i] = _totalColor
                    pieData[i]=1;
                } else {
                    pieData[i]=1;
                    colors[i] = _totalColor;
                }
            }                      
        }                     
        var opts={};
        opts.stroke="#ffffff";
        opts.strokewidth=1;
        opts.colors=colors;
        _raphaelHandle.g.piechart(X, Y, Radius, pieData,opts);
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
            _createEquationWithCommonDenominator();                      
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
            } else if (_hintsGiven==2) {
                $("#dvHintText1").css("display","");
                $("#dvHintText1").append("Since these fractions have the same denominator, you can just add the numerators and keep the same denominator.");
            } else if (_hintsGiven==3) {
                $("#dvHintText2").css('color',getNextColor());
                $("#dvHintText2").css("display","");
            } else if (_hintsGiven==4) {
                $("#dvHintText4").css('color',getNextColor());
                $("#dvHintText4").css("display","");
            }
            _hintsGiven++;
            Exercise.steps_given++;
        },

        check_answer: function(){
            var Nominator = document.getElementById("txtNominator").value
            var Denominator = document.getElementById("txtDenominator").value
            if(isNaN(Nominator) || $.trim(Nominator) ==''){
                alert("Enter a valid numerator.");
                $('#txtNominator').focus();
                return Answer.INVALID;
            } else if(_reducedDenominator==1 && $.trim(Denominator) ==''){

            } else if(isNaN(Denominator) || $.trim(Denominator) ==''){
                alert("Enter a valid denominator.");
                return Answer.INVALID;
            }
            var isCorrect = false,temp;           

            if(_reducedDenominator==1 && $.trim(Denominator) ==''){
                isCorrect = (_reducedNominator== Nominator) ;
            }else {
                isCorrect = (_reducedNominator/_reducedDenominator == Nominator/Denominator);
            }
            
            if (isCorrect) {
                return Answer.CORRECT;
            } else {
                $('#txtNominator').focus();
                return Answer.INCORRECT;                
            }
        }
    };
};


$(document).ready(function(){
    FractionAddition.AdditionWithCommonDenominator.init();  
})