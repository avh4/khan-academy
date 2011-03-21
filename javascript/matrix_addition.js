/*
* Author: Gohar-UL-Islam
* Date: 20 Feb 2011
* Description: Matrix addition exercise.
*/
MathJax.HTML.Cookie.Set("menu",{});

/*
 * Confiure LaTeX
 */
MathJax.Hub.Config({
    extensions: ["tex2jax.js"],
    jax: ["input/TeX","output/HTML-CSS"],
    "HTML-CSS": {
        availableFonts:[],
        styles: {
            ".MathJax_Preview": {
                visibility: "hidden"
            }
        },
        Augment: {
            Font: {
                loadError: function (font) {
                    MathJax.Message.Set("Can't load web font TeX/"+font.directory,null,2000);
                    document.getElementById("noWebFont").style.display = "";
                },
                firefoxFontError: function (font) {
                    MathJax.Message.Set("Firefox can't load web fonts from a remote host",null,3000);
                    document.getElementById("ffWebFont").style.display = "";
                }
            }
        }
    }
});


/*
 * Matrix Namespace
 */
Matrix = function(){}

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
    var _wrongChoices = new Array();

    /*Private Methods*/

    /*
     * Function:_createMatrixEqation
     * Access Level: Private
     * Parameters: none
     * Description:Creates a Matrix addition equation.
     */
    var _createMatrixEqation = function(){
        var _wrongMatrixEquation1 = null;
        var _wrongMatrixEquation2 = null;
        var _wrongMatrixEquation3 = null;
        var leftMatrixEquation = null;
        var rightMatrixEquation = null;
        var loopI =0;
        var loopJ =0;

        _row =  Math.abs(get_randomInRange(2,4,0));
        _column =  Math.abs(get_randomInRange(2,4,0));

        _leftMatrix = new Array(_row);
        _rightMatrix = new Array(_row);
        _resultentMatrix = new Array(_row);
        _wrongMatrixEquation1 = new Array(_row);
        _wrongMatrixEquation2 = new Array(_row);
        _wrongMatrixEquation3 = new Array(_row);
        for(loopI=0; loopI < _row; loopI++)
        {
            _leftMatrix[loopI] = new Array(_column);
            _rightMatrix[loopI] = new Array(_column);
            _resultentMatrix[loopI] = new Array(_column);
            _wrongMatrixEquation1 = new Array(_column);
            _wrongMatrixEquation2 = new Array(_column);
            _wrongMatrixEquation3 = new Array(_column);

        }


        leftMatrixEquation = "\\begin{bmatrix}";
        rightMatrixEquation = "\\begin{bmatrix}";
        _resultMatrixEquation = "\\begin{bmatrix}";
        _wrongMatrixEquation1 = "\\begin{bmatrix}";
        _wrongMatrixEquation2 = "\\begin{bmatrix}";
        _wrongMatrixEquation3 = "\\begin{bmatrix}";

        for(loopI=0; loopI < _row; loopI++)
        {
            if(loopI != 0){
                leftMatrixEquation = leftMatrixEquation +  "\\\\";
                rightMatrixEquation = rightMatrixEquation + "\\\\";
                _resultMatrixEquation = _resultMatrixEquation + "\\\\";
                _wrongMatrixEquation1 = _wrongMatrixEquation1 + "\\\\";
                _wrongMatrixEquation2 = _wrongMatrixEquation2 + "\\\\";
                _wrongMatrixEquation3 = _wrongMatrixEquation3 + "\\\\";
            }
            for(loopJ=0; loopJ < _column; loopJ++)
            {
                _leftMatrix[loopI][loopJ] = Math.abs(get_random());
                _rightMatrix[loopI][loopJ] = Math.abs(get_random());
                _resultentMatrix[loopI][loopJ] = _leftMatrix[loopI][loopJ] + _rightMatrix[loopI][loopJ];
                if(loopJ == 0){
                    leftMatrixEquation = leftMatrixEquation + "\\mathbf{" + _leftMatrix[loopI][loopJ]  + "}";
                    rightMatrixEquation = rightMatrixEquation + "\\mathbf{" + _rightMatrix[loopI][loopJ]  + "}";
                    _resultMatrixEquation = _resultMatrixEquation + "\\mathbf{" + _resultentMatrix[loopI][loopJ]  + "}";
                    _wrongMatrixEquation1 = _wrongMatrixEquation1 + "\\mathbf{" +  Math.abs(get_randomInRange(5,18,0))  + "}";
                    _wrongMatrixEquation2 = _wrongMatrixEquation2 + "\\mathbf{" +  Math.abs(get_randomInRange(5,18,0))  + "}";
                    _wrongMatrixEquation3 = _wrongMatrixEquation3 + "\\mathbf{" +  Math.abs(get_randomInRange(5,18,0))  + "}";

                } else {
                    leftMatrixEquation = leftMatrixEquation + " & \\mathbf{" + _leftMatrix[loopI][loopJ]  + "}";
                    rightMatrixEquation = rightMatrixEquation + " & \\mathbf{" + _rightMatrix[loopI][loopJ]  + "}";
                    _resultMatrixEquation = _resultMatrixEquation + " & \\mathbf{" + _resultentMatrix[loopI][loopJ]  + "}";
                    _wrongMatrixEquation1 = _wrongMatrixEquation1 + " & \\mathbf{" +  Math.abs(get_randomInRange(5,18,0))  + "}";
                    _wrongMatrixEquation2 = _wrongMatrixEquation2 + " & \\mathbf{" +  Math.abs(get_randomInRange(5,18,0))  + "}";
                    _wrongMatrixEquation3 = _wrongMatrixEquation3 + " & \\mathbf{" +  Math.abs(get_randomInRange(5,18,0))  + "}";
                }
            }
        }

        setCorrectAnswer(_resultentMatrix);

        leftMatrixEquation = leftMatrixEquation + "\\end{bmatrix}";
        rightMatrixEquation = rightMatrixEquation + "\\end{bmatrix}";
        _resultMatrixEquation = _resultMatrixEquation + "\\end{bmatrix}";

        _wrongMatrixEquation1 = _wrongMatrixEquation1 + "\\end{bmatrix}";
        _wrongChoices.push(_wrongMatrixEquation1);

        _wrongMatrixEquation2 = _wrongMatrixEquation2 + "\\end{bmatrix}";
        _wrongChoices.push(_wrongMatrixEquation2);

        _wrongMatrixEquation3 = _wrongMatrixEquation3 + "\\end{bmatrix}";
        _wrongChoices.push(_wrongMatrixEquation3);
        
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
        var tmpTable="";
        var tmpTableRow="";
        tmpTable ="<table cellspacing='0' cellpadding='2'>";
        for (var i=0; i<_row; i++){
            tmpTableRow +='<tr>';
            for (var j=0; j<_column; j++){
                if(i==0){
                    if(j==0){
                        tmpTableRow += '<td style="border-left:solid 1px black; border-top:solid 1px black;">&nbsp;</td>';
                        tmpTableRow += '<td><input id="txt' + i + '' + j + '" type="text" style="width:25px;" /></td>';

                    } else if(j==_column-1){
                        tmpTableRow += '<td><input id="txt' + i + '' + j + '" type="text" style="width:25px;" /></td>';
                        tmpTableRow += '<td style="border-right:solid 1px black; border-top:solid 1px black;">&nbsp;</td>';

                    } else{
                        tmpTableRow += '<td><input id="txt' + i + '' + j + '" type="text" style="width:25px;" /></td>';
                    }
                } else if(i==_row-1){
                    if(j==0){
                        tmpTableRow += '<td style="border-left:solid 1px black; border-bottom:solid 1px black;">&nbsp;</td>';
                        tmpTableRow += '<td><input id="txt' + i + '' + j + '" type="text" style="width:25px;" /></td>';
                    } else if(j==_column-1){
                        tmpTableRow += '<td><input id="txt' + i + '' + j + '" type="text" style="width:25px;" /></td>';
                        tmpTableRow += '<td style="border-right:solid 1px black; border-bottom:solid 1px black;">&nbsp;</td>';
                    } else{
                        tmpTableRow += '<td><input id="txt' + i + '' + j + '" type="text" style="width:25px;" /></td>';
                    }
                } else {
                    if(j==0){
                        tmpTableRow += '<td style="border-left:solid 1px black;">&nbsp;</td>';
                        tmpTableRow += '<td><input id="txt' + i + '' + j + '" type="text" style="width:25px;" /></td>';
                    } else if(j==_column-1){
                        tmpTableRow += '<td><input id="txt' + i + '' + j + '" type="text" style="width:25px;" /></td>';
                        tmpTableRow += '<td style="border-right:solid 1px black;">&nbsp;</td>';
                    } else{
                        tmpTableRow += '<td><input id="txt' + i + '' + j + '" type="text" style="width:25px;" /></td>';
                    }
                }
            }
            tmpTableRow += '</tr>';
        }
        tmpTable += tmpTableRow  + "</table>";
        $("#dvAnswers").append(tmpTable);
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
            _createMatrixEqation();
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

                if (_hintRow==0 && _hintsGiven==0)
                {
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