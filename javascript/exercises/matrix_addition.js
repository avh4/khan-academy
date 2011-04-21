/*
* Author: Gohar-UL-Islam
* Date: 20 Feb 2011
* Description: Matrix addition exercise.
*/


/*
 * Matrix Namespace
 */
if (typeof Matrix == "undefined") {
    Matrix = function(){}
}
/*
 * Class Name: Addition
 */
Matrix.Addition = new function(){

    /*Private Members*/
    var _hintsGiven = 0;
    var _hintRow = 0;
    var _equation = null;
    var _leftMatrix = null;
    var _rightMatrix = null;
    var _resultentMatrix = null;
    var _row =  null;
    var _column =  null;
    var _resultMatrixEquation = null;


    /*Private Methods*/

    /*
     * Function:_createMatrixEqation
     * Access Level: Private
     * Parameters: none
     * Description:Creates a Matrix addition equation.
     */
    var _createMatrixEquation = function(){
        var leftMatrixEquation = null;
        var rightMatrixEquation = null;

        _row =  Math.abs(getRandomIntRange(2,4));
        _column =  Math.abs(getRandomIntRange(2,4));

        _leftMatrix = KA.Matrix.createMatrix(_row, _column);
        _rightMatrix = KA.Matrix.createMatrix(_row, _column);
        _resultentMatrix = KA.Matrix.createMatrix(_row, _column);

        KA.Matrix.populate(_leftMatrix, _row, _column);
        KA.Matrix.populate(_rightMatrix, _row, _column);

        KA.Matrix.add(_leftMatrix,_rightMatrix, _row, _column, _resultentMatrix, true);
        setCorrectAnswer(_resultentMatrix);
        
        leftMatrixEquation = KA.Matrix.createEquation(_leftMatrix, _row, _column);
        rightMatrixEquation = KA.Matrix.createEquation(_rightMatrix, _row, _column);
        _resultMatrixEquation = KA.Matrix.createEquation(_resultentMatrix, _row, _column);
        
        _equation = "<div style='float:left; font-size:150%'>\\["  + leftMatrixEquation + "+" + rightMatrixEquation + "  =   ?\\]</div>";
        $("#dvQuestion").append(_equation);
        $("#dvHint").append("<div style='float:left; font-size:150%'>\\["  + leftMatrixEquation + "+" + rightMatrixEquation + "  = " + _resultMatrixEquation + "\\]</div>");
    }


    /*
     * Access Level: Private
     * Function: _createAnswers
     * Parameters: none
     * Detail: Display answer options on screen
     */
    var _createAnswers = function(){
        $("#dvAnswers").append(KA.Matrix.answerHtml(_row, _column));
    }
    return {
        /*Public Methods*/

        /*
        * Access Level: Public
        * Function: init
        * Parameters: none
        * Detail: Initialize Matrix Addition Exercise
        */
        init: function(){
            _createMatrixEquation();
            _createAnswers();
        },


        /*
        * Access Level: Private
        * Function: next_step
        * Parameters: none
        * Detail: Create next hint step for user.
        */
        next_step: function(){
            if(_hintRow < _row){

                if (_hintRow==0 && _hintsGiven==0){
                    $("#dvHint .mfenced:eq(2) .mn").css("display","none")
                    $("#dvHint").css("display","")
                }

                $("#dvHint .mfenced:eq(0) span .mn")[(_hintsGiven * _row) + _hintRow].style.color = "Blue"
                $("#dvHint .mfenced:eq(1) span .mn")[(_hintsGiven * _row) + _hintRow].style.color = "Blue"
                $("#dvHint .mfenced:eq(2) span .mn")[(_hintsGiven * _row) + _hintRow].style.color = "Green"
                $("#dvHint .mfenced:eq(2) span .mn")[(_hintsGiven * _row) + _hintRow].style.display = ""

                var digitPosition

                if(_hintsGiven == 0){
                    digitPosition = "1<sup>st</sup> digit of";
                } else if(_hintsGiven == 1){
                    digitPosition = "2<sup>nd</sup> digit of";
                } else if(_hintsGiven == 2){
                    digitPosition = "3<sup>rd</sup> digit of";
                } else if(_hintsGiven == 3){
                    digitPosition = "4<sup>th</sup> digit of";
                }

                if(_hintRow == 0){
                    digitPosition = digitPosition + " 1<sup>st</sup> row";
                } else if (_hintRow== 1){
                    digitPosition = digitPosition + " 2<sup>nd</sup> row";
                } else if (_hintRow== 2){
                    digitPosition = digitPosition + " 3<sup>rd</sup> row";
                } else if (_hintRow== 3){
                    digitPosition = digitPosition + " 4<sup>th</sup> row";
                }

                digitPosition = "<br />Add " + digitPosition + " of both matrices.";
                $("#dvHintText").html(digitPosition)
                _hintsGiven++;
                if(_hintsGiven == _column){
                    _hintsGiven = 0;
                    _hintRow++;
                }
                steps_given++;
            }
        },

        check_answer: function(){
            var isCorrect=true;
            for (var i=0; i<_row; i++){
                for (var j=0; j<_column; j++){
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
    Matrix.Addition.init();
})