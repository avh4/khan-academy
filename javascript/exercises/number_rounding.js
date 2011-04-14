/*
 * Author: Ali Muzaffar Khan
 * Date: 22 March 2011
 * Description: Number Rounding Exercise
 */

/*
 * Class Name: Rounding
 */
Rounding = new function(){

    /*Private Members*/
    var _number=0;
    var _correctAnswer=0;
    var _stringNumber='';
    var _numberLength='';
    var _numberArray=[];
    var _xAxis=[];
    var _yAxis=[];
    var _x1,_x2;
    var _roundingType = [
    "ten",
    "hundred",
    "thousand"
    ];

    var _roundingTypeDecimal=[
    'tenth',
    'hundredth',
    'thousandth'
    ]
    var _combinations=[    
    "----",
    "---",
    "--",
    "-.--",
    "-.---",
    "-.----"
    ];
    var _hints = new Array();
    var _divider;
    var _cutOff; //1= unit rounding ,2= tens rounding , 3= thousands rounding
    var _hintStep = 0;
    var _roudingTypeToUse = "";
    var _onScale=false;
    var _hasDecimal=false;
    var _numberValid=false;
    var _raphaelHolder = Raphael("holder",850,150);
    var _lines=null;
    var _isCentered=false;
    var _fractionPart=null;
    var _intPart=null;
    var _highlightIndex=null;
   
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
     * Function:_createNumber
     * Access Level: Private
     * Parameters: none
     * Description: This function generates the number for the problem
     */

    var _createNumber = function(){
        var lStringifiedNumber = '';
        _combinations.sort( _randOrder );        
        var combination = _combinations[getRandomIntRange(0,5)];
        var combinationLength=combination.length;
        var decimalIndex;
        var roudingTypeMaxRange=0;

        for(var i=0; i<combinationLength; i++){
            if(combination.substring(i,i+1)=="-"){
                lStringifiedNumber += (getRandomIntRange(1,8)).toString();
                _numberArray[i]=parseInt(lStringifiedNumber[i]);
            } else {
                lStringifiedNumber += combination.substring(i,i+1);
                _numberArray='.';
            }
        }       

        _number=parseFloat(lStringifiedNumber);
        _stringNumber=lStringifiedNumber;
        _numberLength=lStringifiedNumber.length;

        decimalIndex=lStringifiedNumber.indexOf('.', 0);

        if(decimalIndex==-1){
            if(_number < 100){
                roudingTypeMaxRange=0;
            } else if(_number < 1000){
                roudingTypeMaxRange=1;
            } else if(_number < 10000){
                roudingTypeMaxRange=2;
            }

            _roudingTypeToUse = _roundingType[getRandomIntRange(0,roudingTypeMaxRange)];
        }//if not decimal
        else{
            _hasDecimal=true;
            if(combinationLength==4)
            {
                roudingTypeMaxRange=0;
            } else if(combinationLength==5){
                roudingTypeMaxRange=1;

            } else if(combinationLength>5){
                roudingTypeMaxRange=2;

            }
            _roudingTypeToUse = _roundingTypeDecimal[getRandomIntRange(0,roudingTypeMaxRange)];

        }//if decimal is included
        
    }

    /*
     * Access Level: Private
     * Function: _createProblem
     * Parameters Name: none
     *
     * Description: This function determines the type of rounding
     */
    var _createProblem = function(){
        do{
            _createNumber();            
            var roundPortion;
            switch (_roudingTypeToUse){
                case 'ten':
                    _cutOff=1;
                    _divider=0;
                    _highlightIndex=_numberArray[_numberLength-_cutOff];

                    break;

                case 'hundred':
                    _cutOff=2;
                    _divider=10;
                    break;

                case 'thousand':
                    _cutOff=3;
                    _divider=100;
                    break;

                case 'tenth':
                    _cutOff=1;
                    _fractionPart=_stringNumber.substring(2,3);
                    _highlightIndex=_stringNumber.substring(3,4);
                    break;


                case 'hundredth':
                    _cutOff=1;
                    _fractionPart=_stringNumber.substring(2,4);
                    _highlightIndex=_stringNumber.substring(4,5);
                    break;


                case 'thousandth':
                    _cutOff=1;
                    _fractionPart=_stringNumber.substring(2,5);
                    _highlightIndex=_stringNumber.substring(5,6);
                    break;
            }

            _hints[0]='The two closest '+_roudingTypeToUse+'s to ' + _number + ' are';

            // below code checks if the number is not already or is to small to be displayed on the scale for hints
            
            if(_hasDecimal){
                roundPortion=_stringNumber.substring(3,3+_cutOff);
                _intPart=_stringNumber.substring(0,1);
                
            } else{
                roundPortion=_stringNumber.substring(_stringNumber.length-_cutOff,_stringNumber.length);
            }
            if(roundPortion=='0' || roundPortion=='00' || roundPortion=='000' ){
                _numberValid=false;
            } else if(_cutOff==3 && roundPortion[0]=='0' && parseInt(ltrim(roundPortion.substring(1,2),'0'))<30 ){
                _numberValid=false;
            } else if(_cutOff==2 && roundPortion[0]=='0' && parseInt(ltrim(roundPortion.substring(1,1),'0'))<3 ){
                _numberValid=false;
            } else {
                _numberValid=true;
            }
        }while(!_numberValid)

        $("#dvQuestion").append('Round '  + _number + ' to the nearest ' + _roudingTypeToUse + '.');

    }

    /*
 * Access Level: Private
 * Function: _createAnswer
 * Parameter Name: none
 *
 * Description: sets the correct answer
 */
    var _createAnswer = function() {
        var numberInStr = _number.toString();
        var numberToRound = 0;
        var addToRoundUp = 0;
        var subtractToRoundDown = 0;
        var doRoundUp = false;
        var doRoundDown = false;
   
        if(_roudingTypeToUse=="ten"){
            numberToRound = parseInt(ltrim(numberInStr.substr(numberInStr.length - 2),'0'));

            addToRoundUp = 10 - (numberToRound%10);
            subtractToRoundDown = numberToRound%10;

            if(numberToRound%10 >= 5){
                doRoundUp = true;
            } else{
                doRoundDown=true;
            }
        } else if(_roudingTypeToUse == "hundred"){
            numberToRound = parseInt(ltrim(numberInStr.substr(numberInStr.length - 3),'0'));

            addToRoundUp = 100 - (numberToRound%100);
            subtractToRoundDown = numberToRound%100;

            if(numberToRound%100 >= 50){
                doRoundUp = true;
            } else{
                doRoundDown=true;
            }
        } else if(_roudingTypeToUse == "thousand"){
            numberToRound = parseInt(ltrim(numberInStr.substr(numberInStr.length - 4),'0'));


            addToRoundUp = 1000 - (numberToRound%1000);
            subtractToRoundDown = numberToRound%1000;

            if(numberToRound%1000 >= 500){
                doRoundUp = true;
            } else{
                doRoundDown=true;
            }
        } else{
            _correctAnswer=parseFloat(_intPart+'.'+_fractionPart);
            if(_highlightIndex>4){
                _correctAnswer=parseFloat(_intPart+'.'+(parseInt(_fractionPart)+1));
            }
            setCorrectAnswer(_correctAnswer);
            return;
        }

        if(doRoundUp){
            _correctAnswer = _number + addToRoundUp;
        } else if(doRoundDown){
            _correctAnswer = _number - subtractToRoundDown;
        }

        setCorrectAnswer(_correctAnswer);
    }


    /*
     * Function:_generateAxis
     * Access Level: Private
     * Parameters: none
     * Description: This function generates the the co-ordinates of the axis for drawing the scale
     */

    var _generateAxis = function() {
            
        var i=0,start=0,incStep=1;
        if(!_hasDecimal) {
            start=_number-parseInt(ltrim(_stringNumber.substring(_numberLength-_cutOff,_numberLength),'0'));
        }
        switch(_cutOff){
            case 2:
                incStep=10;
                break;

            case 3:
                incStep=100;
                break;
        }

        for(i=0;i<=10;i++){
            _xAxis[i]=start;
            _yAxis[i]=0;
            start+=incStep;
        }
        
    }// end of axis generator

    /*
     * Function:_generateAxis
     * Access Level: Private
     * Parameters: none
     * Description: This function draws the scale
     */
    
    var _drawScale = function (){
        _generateAxis();
        _lines = _raphaelHolder.g.linechart(15, 100, 800, 25, _xAxis, _yAxis, {
            nostroke: false,
            axis: "0 0 1 0",
            axisxstep:10,
            smooth: true
        });
        _lines.axis[0].text.items[0].attr('fill','#EE8262');
        _lines.axis[0].text.items[10].attr('fill','#EE8262');

        if(_hasDecimal)
        {
            var temp;
            for(i=1;i<=9;i++){
                temp=_intPart+'.'+_fractionPart+i;
                _lines.axis[0].text.items[i].attr('text',temp);

            }

            _lines.axis[0].text.items[0].attr('text',_intPart+'.'+_fractionPart);
            _lines.axis[0].text.items[10].attr('text',_intPart+'.'+(parseInt(_fractionPart)+1));


        }
    }

    /*
     * Function:_setCoordinates
     * Access Level: Private
     * Parameters: none
     * Description: This function sets the co-ordinates for the hint lines that are to be drawn
     */
    
    var _setCoordinates= function(){
        var startIndex;
        if(_cutOff==1){// in case of tens rounding we dont need startIndex and the remianing mathematics is fixed
            startIndex=0;            
            _x1=_highlightIndex*78+15;
            _x2=_highlightIndex*78+25;
            if(_highlightIndex==5){
                _isCentered=true;
            }          

        } else {
            for(i=0;i<=10;i++){
                if(_number<=_xAxis[i]){
                    startIndex=i-1;
                    if(_number==_xAxis[i]){
                        _onScale=true;
                    }
                    break;
                }
            }

            if(_onScale){
                _x1=_numberArray[_numberLength-_cutOff]*78+15;
                _x2=_numberArray[_numberLength-_cutOff]*78+25;
            } else {
                _x1=(startIndex*78+15)+(78*(parseInt(ltrim(_stringNumber.substring(_numberLength-_cutOff+1,_numberLength),'0')))/_divider);
                _x2=(startIndex*78+25)+(78*(parseInt(ltrim(_stringNumber.substring(_numberLength-_cutOff+1,_numberLength),'0')))/_divider) ;
            }
        }
        return startIndex;
    }

    /*
     * Function:_drawLines
     * Access Level: Private
     * Parameters: none
     * Description: This function draws the lines
     */
    
    var _drawLines= function (){
        var firstPathCoOrdinates="M 25 90 H " + _x1 + "  m 0 -5 v 10 l 10 -5";
        var firstPath=_raphaelHolder.path(firstPathCoOrdinates);
        var firstPathReverse=_raphaelHolder.path(firstPathCoOrdinates);
        firstPathReverse.rotate(180);

        firstPath.attr({
            fill: '#000',
            stroke: '#000',
            'stroke-width': 1
        });

        firstPathReverse.attr({
            fill: '#000',
            stroke: '#000',
            'stroke-width': 1
        });

        var secondPathCoOrdinates="M " + _x2 + " 90 H 795  m 0 -5 v 10 l 10 -5";
        var secondPath=_raphaelHolder.path(secondPathCoOrdinates);
        var secondPathReverse=_raphaelHolder.path(secondPathCoOrdinates);

        secondPathReverse.rotate(180);

        secondPath.attr({
            fill: '#000',
            stroke: '#000',
            'stroke-width': 1
        });
        secondPathReverse.attr({
            fill: '#000',
            stroke: '#000',
            'stroke-width': 1
        });        
    }

    /*
     * Function:_createHints
     * Access Level: Private
     * Parameters: none
     * Description: This function handles the flow of hints 
     */
    

    var _createHint = function(){
        var startIndex;
        if(_hintStep==0)
        {
            _drawScale();

        }else if(_hintStep==1){
            startIndex=_setCoordinates();
            if(_cutOff>1 && !_onScale){

                var numCoOrdinates="M " + _x2 + " 110 v 5";
                var numPath=_raphaelHolder.path(numCoOrdinates);
                numPath.attr({
                    fill: '#CFD784',
                    stroke: '#CFD784',
                    'stroke-width': 1
                });

                var text = _raphaelHolder.text(_x2, 105, _number);
                text.attr('fill','#CFD784');
            } else if(_cutOff>1 && _onScale) {
                _lines.axis[0].text.items[startIndex+1].attr('fill','#CFD784');

                if(startIndex+1==5){
                    _isCentered=true;
                }
            }

            if(_cutOff==1){              
                _lines.axis[0].text.items[_highlightIndex].attr('fill','#CFD784');
               
            }
        }//end of step 2

        //begin step3 at this point we draw the arrow heads above
        if(_hintStep>1){

            _drawLines();

            _hints[1]="Whats nearest to <strong>" + Number + "</strong> ? " + _xAxis[0] + " or "+_xAxis[10];
            _hints[2]="Whats nearest to <strong>" + Number + "</strong> ? " + _xAxis[0] + " or "+_xAxis[10];

        }//hint for step 2 closed draws the arrow heads in this case

        if(_isCentered && _hintStep==1){
            $('#dvAnswer').html("Since the value to be rounded lies exactly between " + _xAxis[0] + " and " + _xAxis[10] + " , therefore we round to the higher boundary");
            $('#dvAnswer').css('display','block');
        }

    }//end of _createhint


    return{
        init: function(){
            _createProblem();            
            _createAnswer();
        },
        next_step: function (){
            $('#dvHint').css('display','block');

            if(_hintStep<3){
                $('#dvHint').html(_hints[_hintStep]);
                _createHint();                
            } else if(_hintStep==3) {
                if(_isCentered){
                    var answerHtml=$('#dvAnswer').html();
                    $('#dvAnswer').html(answerHtml+="<br/><br/><strong>Answer " + _correctAnswer + "</strong>");
                } else {
                    $('#dvAnswer').html("<strong>Answer "+_correctAnswer+"</strong> is the nearest "+_roudingTypeToUse +", so we round <strong>"+_number+"</strong> to <span style='text-decoration:underline'><strong>"+_correctAnswer+"</strong></span>");
                }
                $('#dvAnswer').css('display','block');
            }
            _hintStep++;
            steps_given++;
        }
    }
};
$(document).ready(function(){
    Rounding.init();
})