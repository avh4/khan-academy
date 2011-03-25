/*
 * Author: Gohar-UL-Islam
 * Date: 21 Feb 2011
 * Description: Fraction Subtraction exercise with common dinominators.
 */

/*
 * Class Name: Rounding
 */
Rounding = new function(){
    var _number=0;
    var _correctAnswer=0;
    var _wrongAnswer= new Array();
    var _roundingType = [
    "Tenth",
    "Hundredth",
    "Thousandth",
    ];
    var _hints = new Array();
    var _divider;
    var _cutOff; //1= unit rounding ,2= tens rounding , 3= thousands rounding
    var _hintStep = 0;
    var _roudingTypeToUse = "";    
    var _onScale=false;
    var _numberValid=false;
    var _raphaelHolder = Raphael("holder",850,150);
    var _lines=null;
    var _isCentered=false;
    /*Private Members*/

    /*
     * Access Level: Private
     * Function: _createChoice
     * Parameters Name: none
     *
     * Description: Generates the number for rounding
     */
    var _createProblem = function(){
        do{
            _number = get_randomInRange(11,30000,0);
            var roudingTypeMaxRange=0;

            if(_number < 100){
                roudingTypeMaxRange=0;

            } else if(_number < 1000){
                roudingTypeMaxRange=1;

            } else if(_number < 10000){
                roudingTypeMaxRange=2;

            }
            _roudingTypeToUse = _roundingType[get_randomInRange(0,roudingTypeMaxRange,0)];
            switch (_roudingTypeToUse)
            {

                case 'Tenth':
                    _cutOff=1;
                    _hints[0]='The two closest tens to '+_number+' are';
                    _divider=0;
                    break;

                case 'Hundredth':
                    _cutOff=2;
                    _hints[0]='The two closest hundreds to '+_number+' are';
                    _divider=10;
                    break;

                case 'Thousandth':
                    _cutOff=3;
                    _hints[0]='The two closest thousands to '+_number+' are';
                    _divider=100;
                    break;
            }
            // below code checks if the number is not already or is to small to be displayed on the scale for hints
            var strNumber=_number.toString();
            var roundPortion=strNumber.substring(strNumber.length-_cutOff,strNumber.length);
            if(roundPortion=='0' || roundPortion=='00' || roundPortion=='000' ){
                _numberValid=false;                
            }
            else if(_cutOff==3 && roundPortion[0]=='0' && parseInt(_ltrim(roundPortion.substring(1,2),'0'))<30 )
            {
                _numberValid=false;
            }
            else if(_cutOff==2 && roundPortion[0]=='0' && parseInt(_ltrim(roundPortion.substring(1,1),'0'))<3 )
            {
                _numberValid=false;
            }
            else{
                _numberValid=true;
            }

        }while(!_numberValid)
        $("#dvQuestion").append('Round '  + _number + ' to the nearest ' + _roudingTypeToUse + '.');
    //_createHint(_number,_roudingTypeToUse);

        
    }

    /*
     * Access Level: Private
     * Function: _createChoice
     * Parameter Name: none
     *
     * Description: sets the correct answer
     */
    var _creteChoices = function() {
        //@ToDo Refector to implement generic solution
        var numberInStr = _number.toString();
        var numberToRound = 0;
        var addToRoundUp = 0;
        var subtractToRoundDown = 0;
        var doRoundUp = false;
        var doRoundDown = false;
        if(_roudingTypeToUse=="Tenth"){
            numberToRound = parseInt(_ltrim(numberInStr.substr(numberInStr.length - 2),'0'));

            addToRoundUp = 10 - (numberToRound%10)
            subtractToRoundDown = numberToRound%10;

            if(numberToRound%10 >= 5){
                doRoundUp = true;
            } else{
                doRoundDown=true;
            }
        } else if(_roudingTypeToUse == "Hundredth"){
            numberToRound = parseInt(_ltrim(numberInStr.substr(numberInStr.length - 3),'0'));

            addToRoundUp = 100 - (numberToRound%100)
            subtractToRoundDown = numberToRound%100;

            if(numberToRound%100 >= 50){
                doRoundUp = true;
            } else{
                doRoundDown=true;
            }
        } else if(_roudingTypeToUse == "Thousandth"){
            numberToRound = parseInt(_ltrim(numberInStr.substr(numberInStr.length - 4),'0'));


            addToRoundUp = 1000 - (numberToRound%1000)
            subtractToRoundDown = numberToRound%1000;

            if(numberToRound%1000 >= 500){
                doRoundUp = true;
            } else{
                doRoundDown=true;
            }
        }
        
        if(doRoundUp){
            _correctAnswer = _number + addToRoundUp
            _wrongAnswer.push(_number - subtractToRoundDown)
        } else if(doRoundDown){
            _correctAnswer = _number - subtractToRoundDown
            _wrongAnswer.push(_number + addToRoundUp)
        }
        setCorrectAnswer(_correctAnswer);
    }
    
    var _ltrim = function  (str, chars) {
        var result;
        chars = chars || "\\s" || "\\.";
        result= str.replace(new RegExp("^[" + chars + "]+", "g"), "");
        if(result=='')
            return 0;
        else
            return result;
    }


    /*
     * Access Level: Private
     * Function: _createHint
     * Parameter1 Name: pNumber
     * Parameters1 Type: integer
     * Parameters1 Detail: This is the number we are trying to round
     *
     * Parameter2 Name: pCutOff
     * Parameters2 Type: integer
     * Parameters2 Detail: This value is equal to the private Variable _cutOff used to determine kind of rounding and in string manipulation
     *
     * Parameter3 name: pRapahel
     * Parameters3 Type: object
     * Parameters3 Detail: This is handle of Raphael
     *
     * Parameter4 name: pHintNumber
     * Parameters4 Type: integer
     * Parameters4 Detail: This number tells which step we are doing of the hint at the moment
     *     
     * Description: Draws the Hints
     */
    var _createHint = function(pNumber,pCutOff,pRaphael,pHintNumber)
    {
        var strNumber=pNumber.toString();
        var arrNumber= new Array();
        var i=0,start,incStep,startIndex,x1,x2;
        var numLength=strNumber.length;
        for(;i<numLength;i++)
        {
            arrNumber[i]=parseInt(strNumber[i]);
                
        }
        //the starting number from where x-axis should begin
        start=pNumber-parseInt(_ltrim(strNumber.substring(numLength-pCutOff,numLength),'0'));
        
        xArray=new Array();
        yArray= new Array();
        switch(pCutOff)
        {
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
       
        for(i=0;i<=10;i++)
        {
            xArray[i]=start;
            yArray[i]=0;
            start+=incStep;
       
        }

        if(pCutOff==1)
        {   // in case of tens rounding we dont need startIndex and the remianing mathematics is fixed
            startIndex=0;            
            x1=arrNumber[numLength-pCutOff]*78+15;
            x2=arrNumber[numLength-pCutOff]*78+25;
            if(arrNumber[numLength-pCutOff]==5){
                _isCentered=true;
            }
        }
        else
        {

            for(i=0;i<=10;i++){
                if(pNumber<=xArray[i]){
                    startIndex=i-1;
                    if(pNumber==xArray[i])
                    {
                        _onScale=true;
                    }
                    break;
                }
            }   
            if(_onScale)
            {
                x1=arrNumber[numLength-pCutOff]*78+15;
                x2=arrNumber[numLength-pCutOff]*78+25;
            }
            else
            {
                x1=(startIndex*78+15)+(78*(parseInt(_ltrim(strNumber.substring(numLength-pCutOff+1,numLength),'0')))/_divider);
                x2=(startIndex*78+25)+(78*(parseInt(_ltrim(strNumber.substring(numLength-pCutOff+1,numLength),'0')))/_divider) ;
            }
        }
        start=xArray[0];

        if(_lines==null)
        {
            _lines = pRaphael.g.linechart(15, 100, 800, 25, xArray, yArray, {
                nostroke: false,
                axis: "0 0 1 0",
                axisxstep:10,
                smooth: true
            });
        }
       
        if(pHintNumber>0)
        {
            
            var firstPathCoOrdinates="M 25 90 H "+x1+"  m 0 -5 v 10 l 10 -5";
            var firstPath=pRaphael.path(firstPathCoOrdinates);
            var firstPathReverse=pRaphael.path(firstPathCoOrdinates);
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
      
            var secondPathCoOrdinates="M "+x2+" 90 H 795  m 0 -5 v 10 l 10 -5";
            var secondPath=pRaphael.path(secondPathCoOrdinates);
            var secondPathReverse=pRaphael.path(secondPathCoOrdinates);
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

            _hints[1]="Whats nearest to <strong>"+pNumber+"</strong> ? "+xArray[0]+" or "+xArray[10];

            if(pCutOff>1 && !_onScale)
            {
                var numCoOrdinates="M "+ x2+" 110 v 5";
                var numPath=pRaphael.path(numCoOrdinates);
                numPath.attr({
                    fill: '#000',
                    stroke: '#000',
                    'stroke-width': 1                    
                });

                var text = pRaphael.text(x2, 105, pNumber,{
                    'fill':'#0f0'
                }); 
            }
            else if(pCutOff>1 && _onScale)
            {
                _lines.axis[0].text.items[startIndex+1].attr('fill','#0F0');

                if(startIndex+1==5){
                    _isCentered=true;
                }


            }


        }
        _lines.axis[0].text.items[0].attr('fill','#F00');
        _lines.axis[0].text.items[10].attr('fill','#F00');
        if(pCutOff==1){
            _lines.axis[0].text.items[arrNumber[numLength-pCutOff]].attr('fill','#0F0');
        }

        if(_isCentered && pHintNumber==1){            
            $('#dvAnswer').html("Since the value to be rounded lies exactly between "+xArray[0]+" and "+xArray[10]+" , therefore we round to the higher boundary");
            $('#dvAnswer').css('display','block');
        }
    
    }//end of _createhint


    return{
        init: function(){
            _createProblem();
            _creteChoices();
        },
        next_step: function (){
            $('#dvHint').css('display','block');
            if(_hintStep<1)
            {                
                $('#dvHint').html(_hints[0]);
                _createHint(_number,_cutOff,_raphaelHolder,0 );                
                _hintStep++;
            }
            else if(_hintStep==1)
            {                
                _createHint(_number,_cutOff,_raphaelHolder,0 );                
                $('#dvHint').html(_hints[1]);
                _hintStep++;
            }
            else if(_hintStep==2){
                if(_isCentered){
                    var answerHtml=$('#dvAnswer').html();
                    $('#dvAnswer').html(answerHtml+="<br/><br/><strong>Answer "+_correctAnswer+"</strong>");
                }
                else{
                    $('#dvAnswer').html("<strong>Answer "+_correctAnswer+"</strong> is nearest so we round <strong>"+_number+"</strong> to <span style='text-decoration:underline'><strong>"+_correctAnswer+"</strong></span>");
                }
                $('#dvAnswer').css('display','block');
                _hintStep++;
            }
            steps_given++;
        }
    }
};
$(document).ready(function(){
    Rounding.init();
})