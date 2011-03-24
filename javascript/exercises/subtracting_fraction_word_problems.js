/*
 * Author: Gohar-UL-Islam
 * Date: 10 Mar 2011
 * Description: Fraction Subtraction word problem.
 */

/*
 * Fraction Subtraction Namespace
 */
FractionSubtraction= function(){}

/*
 * Class Name: SubtractionWordProblem
 */
FractionSubtraction.SubtractionWordProblem = new function(){
    /*Private Members*/
    var _hintsGiven = 0;
    var _num1 = null;
    var _num2 = null;
    var _den1 = null;
    var _den2 = null;
    var _commonDenominator;
    var _equation = null;
    var _wordProblem = [
    "I bought [fraction1] gallons of paint but I only used [fraction2] gallons of the paint. How much paint do I have left?",
    "With my [fraction1] chocolate bar, I gave my sister [fraction2], how much do I have left?",
    "[fraction1] mini pizzas were left in the fridge, the kids ate [fraction2] of them. How much pizza is left for the adults?",
    "In my garden, I planted [fraction1] rows of seeds. The crows came along and ate [fraction2] rows of the seeds. What's left of my rows of seeds?",
    "We had [fraction1] of a pizza left when we went to bed. The next morning [fraction2] of what was left had been eaten. how much pizza is left?",
    'I had [fraction1] gallons of paint and used [fraction2] gallons to paint my bedroom. How much paint do I have left?',
    "My glass had [fraction1] of a cup of apple juice left in it. I drank [fraction2] of it, how much is left?",
    "Bruce studies for [fraction1] hours daily. He devotes [fraction2] hours of his time for Science and Mathematics. How much time does he devote for other subjects?",
    "Jack and Jill picked up [fraction1] cherries. If Jack picked up [fraction2] cherries how many did Jill pick up? ",    
    "Customer's goods total to an amount of [fraction1] dollars and customer gives cashier an amount of [fraction2] dollars. How much money customer still owe the cashier?",
    "Anthony and Emily were in a spelling bee. Anthony spelled [fraction1] words correctly. Emily spelled [fraction2] words correctly. How many more words did Emily spell correctly?",
    "Chris had [fraction1] cupcakes. Danial ate [fraction2] of them. how many cupcakes Chris have left?",
    "A bowl has [fraction1] M&Ms in it. Rachael ate [fraction2] of them. How many are left in the bowl?",
    "Sam brought [fraction1] pizzas. Dean ate [fraction2] of them. How much of the pizza is left?",
    "Adam bought [fraction1] doughnuts and ate [fraction2] of them. How many are still left?",
    "A recipe needs [fraction1] teaspoon black pepper and [fraction2] red pepper. How much more black pepper does the recipe need?",
    "A football player advances [fraction2] of a yard. A second player in the same team advances [fraction1] of a yard. How much more yard did the second player advance?",
    "John lives [fraction1] mile from the Museum of Science. Sylvia leaves [fraction2] mile from the Museum of Science. How much closer is Sylvia from the museum?"
    ];
    var _raphaelHandle = Raphael('holder',500,200);

    /*Private Methods*/

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
     * Function:_createEquationWithCommonDenominator
     * Access Level: Private
     * Parameters: none
     * Description:Creates a fraction subtraction word problem.
     */
    var _createEquationWithCommonDenominator = function(){
        _wordProblem.sort( _randOrder );
        _num1 = Math.abs(get_random());
        _num2 = Math.abs(get_random());
        if(_num1 < _num2){
            _den1 = getRandomIntRange(_num2,_num2 + 10);
        } else {
            _den1 = getRandomIntRange(_num1,_num1 + 10);
        }
        _den2 = _den1;
        _commonDenominator = _den2;
        if(_num1 < _num2){
            var _tmpNum = _num2;
            _num2 = _num1;
            _num1 = _tmpNum;
        }
        var fractionEquation1= "`"+ _num1 + "/" + _den1 + "`";
        var fractionEquation2= "`" + _num2 + "/" + _den2 + "`";
        var wordproblem = _wordProblem[getRandomIntRange(0,_wordProblem.length-1)];
        wordproblem = wordproblem.replace("[fraction1]",fractionEquation1);
        wordproblem = wordproblem.replace("[fraction2]",fractionEquation2);
        _equation = wordproblem;
        $("#dvHintText2").append('`?/' + _den1 + '`')
        if(_num1>_num2){
            $("#dvHintText4").append("`"+ _num1 + "/" + _den1 + "` `-` `" + _num2 + "/" + _den2 + "`" + " &nbsp;&nbsp;`=` &nbsp;&nbsp;`" + ((_num1*_commonDenominator/_den1)-(_num2*_commonDenominator/_den2)) + "/" + _commonDenominator + "`");
        } else {
            $("#dvHintText4").append("`"+ _num2 + "/" + _den1 + "` `-` `" + _num1 + "/" + _den2 + "`" + " &nbsp;&nbsp;`=` &nbsp;&nbsp;`" + ((_num2*_commonDenominator/_den1)-(_num1*_commonDenominator/_den2)) + "/" + _commonDenominator + "`");
        }
        _writeEquation("#dvQuestion", _equation, false);
        setCorrectAnswer((_num1*_commonDenominator/_den1)-(_num2*_commonDenominator/_den2) + "/" + _commonDenominator);

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
     * Function: _createAnswers
     * Parameters: none
     * Detail: Display answer options on screen
     */
    var _createAnswers = function(){
        $("#dvAnswers").append("<div><div style='padding-left: 7px;'><input id='txtNominator' type='text' style='width:25px;'/></div><div style='width: 43px; border-top: solid 3px black;'></div><div style='padding-left: 7px;'><input id='txtDenominator' type='text' style='width:25px;' /></div></div>");
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
    var _createHint =function(MyShare, MyTotal, X, Y, Radius) {
        
        var pieData=new Array();
        var colors=new Array();
        for ( var i = 0; i < MyTotal; i++) {
            if (i < MyShare) {
                if (i % 2){
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
        _raphaelHandle.g.piechart(X, Y, Radius, pieData,opts);
        
    }
    return {
        /*Public Methods*/

        /*
         * Access Level: Public
         * Function: init
         * Parameters: none
         * Detail: Initialize Fraction subtraction Exercise
         */
        init: function(){
            _createEquationWithCommonDenominator();
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
                _createHint(_num2, _den2,  320, 95,  90,'holder');
            } else if (_hintsGiven==2) {
                $("#dvHintText1").css("display","");
                $("#dvHintText1").append("Since these fractions both have the same denominator, the difference is going to have the same denominator.");
            } else if (_hintsGiven==3) {
                $("#dvHintText2").css("display","");
            } else if (_hintsGiven==4) {
                $("#dvHintText3").css("display","");
                $("#dvHintText3").append("The numerator is simply going to be the difference of the numerators");
            } else if (_hintsGiven==5) {
                $("#dvHintText4").css("display","");
            }
            _hintsGiven++;
            steps_given++;
        },

        check_answer: function(){
            var Nominator = document.getElementById("txtNominator").value
            var Denominator = document.getElementById("txtDenominator").value
            if(isNaN(Nominator) || $.trim(Nominator) ==''){
                alert("Enter valid nominator.");
                return;
            } else if(isNaN(Denominator) || $.trim(Denominator) ==''){
                alert("Enter valid dinominator.");
                return;
            }
            var isCorrect = false;
            isCorrect = (correct_answer == (Nominator  + "/" + Denominator));
            handleCorrectness(isCorrect);
        }
    };
};
$(document).ready(function(){
    FractionSubtraction.SubtractionWordProblem.init();
})