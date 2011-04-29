/*
* Author: Gohar-UL-Islam
* Date: 20 Feb 2011
* Description: Matrix Multiplication exercise.
*/



/*
 * Matrix Namespace
 */
if (typeof Matrix == "undefined") {
    Matrix = function(){}
}

/*
 * Class Name: Multiplication
 */
Matrix.Multiplication = new function(){
    /*Private Members*/
    var _hintsGiven = 0;
    var _TotalHintsGiven = 0;
    var _hintLeftMatrixRow = 0;
    var _hintRightMatrixColumn = 0;
    var _hintResultentMatrixColumn = 0;
    var _equation = null;

    var _leftMatrix = null;
    var _rightMatrix = null;
    var _resultentMatrix = null;

    var _LeftMatrixRow =  null;
    var _RightMatrixRow =  null;
    var _LeftMatrixColumn =  null;
    var _RightMatrixColumn =  null;
    var _hintMultiplicationArray;
    var _resultMatrixEquation = null;



    /*Private Methods*/

    /*
     * Function:_createMatrixEqation
     * Access Level: Private
     * Parameters: none
     * Description:Creates a Matrix Multiplication equation with common dinominators
     */
    var _createMatrixEquation = function(){
        var leftMatrixEquation = null;
        var rightMatrixEquation = null;
        
        _LeftMatrixRow =  Math.abs(getRandomIntRange(2,4));
        _LeftMatrixColumn =  Math.abs(getRandomIntRange(2,4));
        _RightMatrixRow = _LeftMatrixColumn;
        _RightMatrixColumn = Math.abs(getRandomIntRange(2,4));
       
        _hintMultiplicationArray = new Array(_LeftMatrixColumn);
        _leftMatrix = KA.Matrix.createMatrix(_LeftMatrixRow, _LeftMatrixColumn);
        _rightMatrix = KA.Matrix.createMatrix(_RightMatrixRow, _RightMatrixColumn);
        _resultentMatrix = KA.Matrix.createMatrix(_LeftMatrixRow, _RightMatrixColumn);

        KA.Matrix.populate(_leftMatrix, _LeftMatrixRow, _LeftMatrixColumn);
        KA.Matrix.populate(_rightMatrix, _RightMatrixRow, _RightMatrixColumn);
        KA.Matrix.multiply(_leftMatrix, _LeftMatrixRow, _LeftMatrixColumn, _rightMatrix, _RightMatrixColumn, _resultentMatrix);
        setCorrectAnswer(_resultentMatrix);

        leftMatrixEquation = KA.Matrix.createEquation(_leftMatrix, _LeftMatrixRow, _LeftMatrixColumn);
        rightMatrixEquation = KA.Matrix.createEquation(_rightMatrix, _RightMatrixRow, _RightMatrixColumn);
        _resultMatrixEquation = KA.Matrix.createEquation(_resultentMatrix, _LeftMatrixRow, _RightMatrixColumn);
                
        _equation = "<div style='float:left; font-size:150%'>\\["  + leftMatrixEquation + "*" + rightMatrixEquation + "  = ?\\]</div>";
        $("#dvQuestion").append(_equation);
        $("#dvHint").append("<div style='float:left; font-size:150%'>\\["  + leftMatrixEquation + "*" + rightMatrixEquation + "  = " + _resultMatrixEquation + "\\]</div>");
    }



    /*
     * Access Level: Private
     * Function: _createAnswers
     * Parameters: none
     * Detail: Display answer options on screen
     */
    var _createAnswers = function(){
        $("#dvAnswers").append(KA.Matrix.answerHtml(_LeftMatrixRow, _RightMatrixColumn));
    }
    return {
        /*Public Methods*/

        /*
        * Access Level: Public
        * Function: init
        * Parameters: none
        * Detail: Initialize Matrix Multiplication Exercise
        */
        init: function(){
            _createMatrixEquation();
            _createAnswers();
        },


        /*
        * Access Level: Public
        * Function: next_step
        * Parameters: none
        * Detail: Create next hint step for user.
        */
        next_step: function(){
            _TotalHintsGiven++;
            if(_TotalHintsGiven == 1){
                $("#dvHintText").html("Resultant Matrix of product of 2 matrices will have rows equal to the rows if Left Matrix and Columns equal to the column of right matrix");
            } else if(_TotalHintsGiven == 2){
                $("#dvHintText").html("The resultant matrix will have 2 Rows & 3 Columns.");
            } else{
                //if(_hintsGiven%_LeftMatrixRow == 0){
                //}
               
                if(_hintsGiven == 0){
                    $("#dvHint .mfenced:eq(2) .mn").css("display","none");
                    $("#dvHint").css("display","");
                }
                var loopI=0;
                if(_hintsGiven < _LeftMatrixRow*_RightMatrixColumn){
                    if(_hintRightMatrixColumn == 0){
                        $("#dvHint .mfenced:eq(0) .mn").css("color","Black");
                        for(loopI=0; loopI<_LeftMatrixColumn; loopI++){
                            if(loopI==0){
                                $("#dvHint .mfenced:eq(0) .mn")[(_LeftMatrixRow * loopI) + _hintLeftMatrixRow].style.color = "Red";
                                _hintMultiplicationArray[loopI] = "<span style='color:red'>" + $("#dvHint .mfenced:eq(0) .mn")[(_LeftMatrixRow * loopI) + _hintLeftMatrixRow].innerText;
                            } else if(loopI==1){
                                $("#dvHint .mfenced:eq(0) .mn")[(_LeftMatrixRow * loopI) + _hintLeftMatrixRow].style.color = "Green";
                                _hintMultiplicationArray[loopI] = "<span style='color:Green'>" + $("#dvHint .mfenced:eq(0) .mn")[(_LeftMatrixRow * loopI) + _hintLeftMatrixRow].innerText;
                            } else if(loopI==2){
                                $("#dvHint .mfenced:eq(0) .mn")[(_LeftMatrixRow * loopI)  + _hintLeftMatrixRow].style.color = "Blue";
                                _hintMultiplicationArray[loopI] = "<span style='color:Blue'>" + $("#dvHint .mfenced:eq(0) .mn")[(_LeftMatrixRow * loopI) + _hintLeftMatrixRow].innerText;
                            } else if(loopI==3){
                                $("#dvHint .mfenced:eq(0) .mn")[(_LeftMatrixRow * loopI)  + _hintLeftMatrixRow].style.color = "Pink";
                                _hintMultiplicationArray[loopI] = "<span style='color:Pink'>" + $("#dvHint .mfenced:eq(0) .mn")[(_LeftMatrixRow * loopI) + _hintLeftMatrixRow].innerText;
                            }
                        }
                    }

                    $("#dvHint .mfenced:eq(1) .mn").css("color","Black");
                    var currentRow="";
                    var currentColumn="";
                    switch (Math.floor(_hintsGiven/_RightMatrixColumn) + 1) {
                        case 1:
                            currentRow = '1<sup>st</sup>';
                            break;
                        case 2:
                            currentRow = '2<sup>nd</sup>';
                            break;
                        case 3:
                            currentRow = '3<sup>rd</sup>';
                            break;
                        case 4:
                            currentRow = '4<sup>th</sup>';
                            break;
                    }
                    switch (Math.floor(_hintsGiven%_RightMatrixColumn) + 1) {
                        case 1:
                            currentColumn = '1<sup>st</sup>';
                            break;
                        case 2:
                            currentColumn = '2<sup>nd</sup>';
                            break;
                        case 3:
                            currentColumn = '3<sup>rd</sup>';
                            break;
                        case 4:
                            currentColumn = '4<sup>th</sup>';
                            break;
                    }
                    for(loopI=0; loopI<_RightMatrixRow; loopI++){
                        if(loopI==0){

                            $("#dvHint .mfenced:eq(1) .mn")[_hintRightMatrixColumn + loopI].style.color = "Red";
                            $("#dvHintText").html("Multiply the " + currentRow + " row of left matrix with the " + currentColumn + " column of right matrix digit by digit and sum the resultant product. <br /><br />");
                            $("#dvHintText").append(_hintMultiplicationArray[loopI] + "x" + $("#dvHint .mfenced:eq(1) .mn")[(_hintRightMatrixColumn + loopI)].innerText);
                        } else if(loopI==1){
                            $("#dvHint .mfenced:eq(1) .mn")[_hintRightMatrixColumn + loopI].style.color = "Green";
                            $("#dvHintText").append(" + " + _hintMultiplicationArray[loopI] + "x" + $("#dvHint .mfenced:eq(1) .mn")[(_hintRightMatrixColumn + loopI)].innerText);
                        } else if(loopI==2){
                            $("#dvHint .mfenced:eq(1) .mn")[_hintRightMatrixColumn + loopI].style.color = "Blue";
                            $("#dvHintText").append(" + " + _hintMultiplicationArray[loopI] + "x" + $("#dvHint .mfenced:eq(1) .mn")[(_hintRightMatrixColumn + loopI)].innerText);
                        } else if(loopI==3){
                            $("#dvHint .mfenced:eq(1) .mn")[_hintRightMatrixColumn + loopI].style.color = "Pink";
                            $("#dvHintText").append(" + " + _hintMultiplicationArray[loopI] + "x" + $("#dvHint .mfenced:eq(1) .mn")[(_hintRightMatrixColumn + loopI)].innerText);
                        }
                    }
                
                    $("#dvHint .mfenced:eq(2) .mn")[_hintResultentMatrixColumn + _hintLeftMatrixRow].style.display = "";
                    $("#dvHint .mfenced:eq(2) .mn")[_hintResultentMatrixColumn + _hintLeftMatrixRow].style.color = "Lime"
                    $("#dvHintText").append(" = <span style='color:Lime'>" + $("#dvHint .mfenced:eq(2) .mn")[_hintResultentMatrixColumn + _hintLeftMatrixRow].innerText  + "</span>");
                    $("#dvHintText").append("<br /><br /> <span style='color:Lime'>" + $("#dvHint .mfenced:eq(2) .mn")[_hintResultentMatrixColumn + _hintLeftMatrixRow].innerText  + "</span> will be placed as " + currentColumn + " element of " + currentRow + " row of resultant matrix. ");

                    _hintResultentMatrixColumn += _LeftMatrixRow;
                    _hintRightMatrixColumn += _LeftMatrixColumn;
                    if(_hintRightMatrixColumn >= (_RightMatrixColumn*_RightMatrixRow)){
                        _hintResultentMatrixColumn = 0;
                        _hintRightMatrixColumn=0;
                        _hintLeftMatrixRow += 1;
                    }                
                    _hintsGiven += 1;
                }
                steps_given++;
                _TotalHintsGiven++;
            } 
        },
        
        check_answer: function(){
            var isCorrect=true;
            for (var i=0; i<_LeftMatrixRow; i++){
                for (var j=0; j<_RightMatrixColumn; j++){
                    if(((correct_answer[i][j]).toString() != document.getElementById('txt' + i + '' + j).value) ){
                        if(isNaN(document.getElementById('txt' + i + '' + j).value)==true){
                            window.alert("Your answer is not a number.  Please try again.");
                        }
                        isCorrect=false;
                        break;
                    }
                }
                if(isCorrect==false)
                    break;
            }
            handleCorrectness(isCorrect);
        }
    };
};


$(document).ready(function(){
    Matrix.Multiplication.init();
})