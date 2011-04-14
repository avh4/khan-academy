/*
 * Author: Ali Muzaffar
 * Date: 10 Mar 2011
 * Description: Fraction Subtraction word problem.
 */


/*
 * Fraction Addition Namespace
 */
FractionAddition= function(){}

/*
 * Class Name: AdditiionWordProblem
 */
FractionAddition.AdditionWordProblem = new function(){
    /*Private Members*/
    
    var _hintsGiven = 0;
    var _num1 = null;
    var _num2 = null;
    var _den1 = null;
    var _den2 = null;
    var _commonDenominator;
    var _reducedNominator;
    var _reducedDenominator;
    var _unreducedNominator;
    var _myColor=getNextColor() ;
    var _totalColor=getNextColor() ;
    var _equation = null;
    var _wordProblem = [
    'At my birthday party, the girls ate [fraction_1] pizzas and the boys ate [fraction_2] pizzas. How many pizzas were eaten at my party?',
    'My recipe calls for [fraction_1] cups of white flour and [fraction_2] cups of whole wheat flour. How much flour do I need in total for my recipe?',
    'During the pie eating contest my dad ate [fraction_1] pies and my mom ate [fraction_2] pies. How many pies did they eat altogether?',
    'I need to drink [fraction_1] cups of water and [fraction_2] cups of milk everyday. How much fluid do I have to drink?',
    'Joey ate [fraction_1] oranges and Billy ate [fraction_2] oranges. They finished all the oranges that were in the bag. How many oranges were in the bag?',
    'If my sister ate [fraction_1] cookies, and I ate [fraction_2]. How many cookies were eaten?',
    'My granola bar recipe calls for [fraction_1] cups of pecans and [fraction_2] cups of walnuts. How many cups of nuts are needed in the recipe?',
    'Jill has [fraction_1] granola bars and Jim has [fraction_2] granola bars. How many granola bars do they have altogether?',
    'If you have [fraction_1] cookie tarts and someone gave you [fraction_2] cookie tarts. How many cookie tarts would you have?',
    'My recipe calls for [fraction_1] cups of white flour and [fraction_2] cups of whole wheat flour. how many cups of flour does the recipe need?',
    'Drew purchased [fraction_1] kg apples and [fraction_2] kg oranges. What is the total weight of fruits purchased by her?',
    'John walked [fraction_1] of a mile yesterday and [fraction_2] of a mile today. How many miles has John walked?',
    'Mary is preparing a final exam. She studies [fraction_1] hours on Friday and [fraction_2] hours on Saturday. How many hours she studied over the weekend?',
    'A recipe requires [fraction_1] teaspoon cayenne pepper and [fraction_2] teaspoon red pepper. How much pepper does this recipe need?',
    'Justin read [fraction_1] pages of his book on Monday. On Tuesday, he read [fraction_2] more pages. How many pages did he read on both days combined?',
    'Martin spent [fraction_1] on a book and [fraction_2] on a candy bar. How much did Martin spend in all?',
    'Justin painted [fraction_1] of the fence on Tuesday and [fraction_2] of fence Wednesday. How much of the fence did he paint in all?',
    'Mike has [fraction_1] of a cake and David has [fraction_2]. How much cake do they have altogether?',
    'Heather goes to the grocery store and spends [fraction_1] dollars for pizza dough, [fraction_2] for mozzarella cheese and a can of pizza sauce. How much did she spend in all?',
    'Eugene has [fraction_1] dollars and Erwin has [fraction_2] dollars. How much money do they have?'
    ];
    var _raphaelHandle = Raphael('holder',500,200);


    /*Private Methods*/

    var _randOrder = function (){
        return (Math.round(Math.random())-0.5);
    }

    /*
     * Function:_createEqationWithCommonDenominator
     * Access Level: Private
     * Parameters: none
     * Description:Creates a fraction Addition word problem.
     */
    var _createEquationWithCommonDenominator = function(){
        var temp;
        _wordProblem.sort( _randOrder );

        _num1 = Math.abs(get_random());
        _num2 = Math.abs(get_random());
        
        if(_num1 < _num2){
            _den1 = getRandomIntRange(_num2,_num2 + 10);
        } else {
            _den1 = getRandomIntRange(_num1,_num1 + 10);
        }
        _den2 = _den1;
        _commonDenominator = getLCM(_den1, _den2);//Get LCM Of Denominators

        var fractionEquation1= "`"+ _num1 + "/" + _den1 + "`";
        var fractionEquation2= "`" + _num2 + "/" + _den2 + "`";
        var questionIndex=getRandomIntRange(0,_wordProblem.length-1);
        var wordproblem = _wordProblem[questionIndex];

        wordproblem = wordproblem.replace("[fraction_1]", fractionEquation1);
        wordproblem = wordproblem.replace("[fraction_2]", fractionEquation2);
        _equation = wordproblem;
        $("#dvHintText2").append('`?/' + _den1 + '`')
        if(_num1>_num2){
            $("#dvHintText4").append("`"+ _num1 + "/" + _den1 + "` `+` `" + _num2 + "/" + _den2 + "`" + " &nbsp;&nbsp;`=` &nbsp;&nbsp;`" + ((_num1*_commonDenominator/_den1)+(_num2*_commonDenominator/_den2)) + "/" + _commonDenominator + "`");
        } else {
            $("#dvHintText4").append("`"+ _num2 + "/" + _den1 + "` `+` `" + _num1 + "/" + _den2 + "`" + " &nbsp;&nbsp;`=` &nbsp;&nbsp;`" + ((_num1*_commonDenominator/_den1)+(_num2*_commonDenominator/_den2)) + "/" + _commonDenominator + "`");
        }
        _writeEquation("#dvQuestion", _equation, false);
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
     * Description:write a fraction addition wordproblem.
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
    var _createHint =function(MyShare, MyTotal, X, Y, Radius) {
        
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
                $("#dvHintText1").css("display","")
                $("#dvHintText1").append("Since these fractions both have the same denominator, the sum is going to have the same denominator.");
            } else if (_hintsGiven==3) {
                $("#dvHintText2").css('color',getNextColor());
                $("#dvHintText2").css("display","");
            } else if (_hintsGiven==4) {
                $("#dvHintText3").css("display","");
                $("#dvHintText3").append("The numerator is simply going to be the sum of the numerators.");
            } else if (_hintsGiven==5) {
                $("#dvHintText4").css('color',getNextColor());
                $("#dvHintText4").css("display","");
            }
            _hintsGiven++;
            steps_given++;
        },

        check_answer: function(){
            var Nominator = document.getElementById("txtNominator").value
            var Denominator = document.getElementById("txtDenominator").value
            if(isNaN(Nominator) || $.trim(Nominator) ==''){
                alert("Enter a valid numerator.");
                $('#txtNominator').focus();
                return ;
            } else if(_reducedDenominator==1 && $.trim(Denominator) ==''){

            } else if(isNaN(Denominator) || $.trim(Denominator) ==''){
                alert("Enter a valid denominator.");
                return ;
            }
            var isCorrect = false,temp;           
            if(_reducedDenominator==1 && $.trim(Denominator) ==''){
                isCorrect = (_reducedNominator== Nominator) ;
            }else {
                temp=get_reduced_fraction(Nominator,Denominator);
                isCorrect = (correct_answer == (temp.numerator  + "/" + temp.denominator));
            }
            handleCorrectness(isCorrect);
            if(!isCorrect){
                $('#txtNominator').focus();
            }
        }
    };
};

$(document).ready(function(){
    FractionAddition.AdditionWordProblem.init();  
})