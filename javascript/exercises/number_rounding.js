/*
 * Author: Ali Muzaffar Khan
 * Date: 22 March 2011
 * Description: Fraction Subtraction exercise with common dinominators.
 */

/*
 * Class Name: Rounding
 */
Rounding = new function(){

    /*Private Members*/
    var _number=0;
    var _correctAnswer=0;
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
            } else {
                lStringifiedNumber += combination.substring(i,i+1);
            }
        }       
        _number=parseFloat(lStringifiedNumber);
        decimalIndex=lStringifiedNumber.indexOf('.', 0);

        if(decimalIndex==-1){
            if(_number < 100){
                roudingTypeMaxRange=0;
            } else if(_number < 1000){
                roudingTypeMaxRange=1;
            } else if(_number < 10000){
                roudingTypeMaxRange=2;
            }
            // _roundingType.sort( _randOrder );
            _roudingTypeToUse = _roundingType[getRandomIntRange(0,roudingTypeMaxRange)];
        }//if not decimal
        else{
            _hasDecimal=true;
            if(combinationLength==4)
            {
                _roudingTypeToUse='tenth';
            } else if(combinationLength==5){
                roudingTypeMaxRange=1;
            //      _roudingTypeToUse='hundredth';
            } else if(combinationLength>5){
                roudingTypeMaxRange=2;
            //    _roudingTypeToUse='thousandth';
            }
            // _roundingTypeDecimal.sort( _randOrder );
            _roudingTypeToUse = _roundingTypeDecimal[getRandomIntRange(0,roudingTypeMaxRange)];

        }//if decimal is included
        
    }

    /*
     * Access Level: Private
     * Function: _createChoice
     * Parameters Name: none
     *
     * Description: Generates the number for rounding
     */
    var _createProblem = function(){
        do{
            _createNumber();
            var strNumber=_number.toString();
            var roundPortion;
            switch (_roudingTypeToUse){
                case 'ten':
                
                    _cutOff=1;
                    _hints[0]='The two closest '+_roudingTypeToUse+'s to ' + _number + ' are';
                    _divider=0;
                    break;

                case 'hundred':
                
                    _cutOff=2;
                    _hints[0]='The two closest '+_roudingTypeToUse+'s to ' + _number + ' are';
                    _divider=10;
                    break;

                case 'thousand':
                
                    _cutOff=3;
                    _hints[0]='The two closest '+_roudingTypeToUse+'s to ' + _number + ' are';
                    _divider=100;
                    break;

                case 'tenth':
                    _cutOff=1;
                    _hints[0]='The two closest '+_roudingTypeToUse+'s to ' + _number + ' are';
                    _divider=0.1;
                    _fractionPart=strNumber.substring(2,3);
                    _highlightIndex=strNumber.substring(3,4);
                    break;


                case 'hundredth':
                    _cutOff=1;
                    _hints[0]='The two closest '+_roudingTypeToUse+'s to ' + _number + ' are';
                    _divider=0.01;
                    _fractionPart=strNumber.substring(2,4);
                    _highlightIndex=strNumber.substring(4,5);
                    break;


                case 'thousandth':
                    _cutOff=1;
                    _hints[0]='The two closest '+_roudingTypeToUse+'s to ' + _number + ' are';
                    _divider=0.001;
                    _fractionPart=strNumber.substring(2,5);
                    _highlightIndex=strNumber.substring(5,6);
                    break;
            }

           
            // below code checks if the number is not already or is to small to be displayed on the scale for hints
            
            if(_hasDecimal){
                roundPortion=strNumber.substring(3,3+_cutOff);
                _intPart=strNumber.substring(0,1);
                
            } else{
                roundPortion=strNumber.substring(strNumber.length-_cutOff,strNumber.length);
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
     * Function: _createChoice
     * Parameter Name: none
     *
     * Description: sets the correct answer
     */
    var _creteAnswer = function() {
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
     * Access Level: Private
     * Function: _createHint
     * Parameter1 Name: Number
     * Parameters1 Type: integer
     * Parameters1 Detail: This is the number we are trying to round
     *
     * Parameter2 Name: CutOff
     * Parameters2 Type: integer
     * Parameters2 Detail: This value is equal to the private Variable _cutOff used to determine kind of rounding and in string manipulation
     *
     * Parameter3 name: Rapahel
     * Parameters3 Type: object
     * Parameters3 Detail: This is handle of Raphael
     *
     * Parameter4 name: HintNumber
     * Parameters4 Type: integer
     * Parameters4 Detail: This number tells which step we are doing of the hint at the moment
     *
     * Description: Draws the Hints
     */
    var _createHint = function(Number,CutOff,Raphael,HintNumber){

        
        var strNumber=Number.toString();
        var arrNumber= new Array();
        var i=0,start,incStep,startIndex,x1,x2;
       

        if(_hasDecimal){            
            strNumber=strNumber.substr(2, CutOff+1);
            Number=parseInt(strNumber);
        }

        var numLength=strNumber.length;
        for(i=0;i<numLength; i++){
            arrNumber[i]=parseInt(strNumber[i]);
        }

        //the starting number from where x-axis should begin
        
        if(_hasDecimal){
            start=0;
        } else{
            start=Number-parseInt(ltrim(strNumber.substring(numLength-CutOff,numLength),'0'));
        }
        var xArray = [];
        var yArray = [];

        switch(CutOff){
            case 1:
                incStep=1;
                break;

            case 2:
                incStep=10;
                break;

            case 3:
                incStep=100;
                break;
        }

        for(i=0;i<=10;i++){
            xArray[i]=start;
            yArray[i]=0;
            start+=incStep;
        }

        

        if(CutOff==1){// in case of tens rounding we dont need startIndex and the remianing mathematics is fixed
            startIndex=0;
            if(_hasDecimal){
                x1=_highlightIndex*78+15;
                x2=_highlightIndex*78+25;
                if(_highlightIndex==5){
                    _isCentered=true;
                }
            }else{
                x1=arrNumber[numLength-CutOff]*78+15;
                x2=arrNumber[numLength-CutOff]*78+25;
                if(arrNumber[numLength-CutOff]==5){
                    _isCentered=true;
                }
            }
            
        } else {
            for(i=0;i<=10;i++){
                if(Number<=xArray[i]){
                    startIndex=i-1;
                    if(Number==xArray[i]){
                        _onScale=true;
                    }
                    break;
                }
            }

            if(_onScale){
                x1=arrNumber[numLength-CutOff]*78+15;
                x2=arrNumber[numLength-CutOff]*78+25;
            } else {
                x1=(startIndex*78+15)+(78*(parseInt(ltrim(strNumber.substring(numLength-CutOff+1,numLength),'0')))/_divider);
                x2=(startIndex*78+25)+(78*(parseInt(ltrim(strNumber.substring(numLength-CutOff+1,numLength),'0')))/_divider) ;
            }
        }
        start=xArray[0];

        if(_lines==null){
            _lines = Raphael.g.linechart(15, 100, 800, 25, xArray, yArray, {
                nostroke: false,
                axis: "0 0 1 0",
                axisxstep:10,
                smooth: true
            });
            _lines.axis[0].text.items[0].attr('fill','#F00');
            _lines.axis[0].text.items[10].attr('fill','#F00');



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

        //begin hint 2 at this point we highlight the number in question
        if(HintNumber==1){
            if(CutOff>1 && !_onScale){

                var numCoOrdinates="M " + x2 + " 110 v 5";
                var numPath=Raphael.path(numCoOrdinates);
                numPath.attr({
                    fill: '#0F0',
                    stroke: '#0F0',
                    'stroke-width': 1
                });

                var text = Raphael.text(x2, 105, Number);
                text.attr('fill','#0F0');
            } else if(CutOff>1 && _onScale) {
                _lines.axis[0].text.items[startIndex+1].attr('fill','#0F0');

                if(startIndex+1==5){
                    _isCentered=true;
                }
            }

            if(CutOff==1){
                if(_hasDecimal){
                    _lines.axis[0].text.items[_highlightIndex].attr('fill','#0F0');
                }else {
                    _lines.axis[0].text.items[arrNumber[numLength-CutOff]].attr('fill','#0F0');
                }
            }
        }//end of step 2

        //begin step3 at this point we draw the arrow heads above
        if(HintNumber>1){

            var firstPathCoOrdinates="M 25 90 H " + x1 + "  m 0 -5 v 10 l 10 -5";
            var firstPath=Raphael.path(firstPathCoOrdinates);
            var firstPathReverse=Raphael.path(firstPathCoOrdinates);
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

            var secondPathCoOrdinates="M " + x2 + " 90 H 795  m 0 -5 v 10 l 10 -5";
            var secondPath=Raphael.path(secondPathCoOrdinates);
            var secondPathReverse=Raphael.path(secondPathCoOrdinates);

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

            _hints[1]="Whats nearest to <strong>" + Number + "</strong> ? " + xArray[0] + " or "+xArray[10];
            _hints[2]="Whats nearest to <strong>" + Number + "</strong> ? " + xArray[0] + " or "+xArray[10];

        }//hint for step 2 closed draws the arrow heads in this case

        if(_isCentered && HintNumber==1){
            $('#dvAnswer').html("Since the value to be rounded lies exactly between " + xArray[0] + " and " + xArray[10] + " , therefore we round to the higher boundary");
            $('#dvAnswer').css('display','block');
        }

    }//end of _createhint


    return{
        init: function(){
            _createProblem();
            _creteAnswer();
        },
        next_step: function (){
            $('#dvHint').css('display','block');

            if(_hintStep<3){
                $('#dvHint').html(_hints[_hintStep]);
                _createHint(_number,_cutOff,_raphaelHolder,_hintStep);
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