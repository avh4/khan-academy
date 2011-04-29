/*
* Author: Gohar-UL-Islam
* Date: 20 Feb 2011
* Description: Fraction determinent exercise.
*/

/*
 * Matrix Namespace
 */
if (typeof Matrix == "undefined") {
    Matrix = function(){}
}

/*
 * Class Name: Determinent
 */
Matrix.Determinant = new function(){

    /*Private Members*/
    var _hintsGiven = 0;
    var _matrix = null;
    var _matrixEquation = null;
    var _row =  3;
    var _column =  3;
    var _equation;
    /*Private Methods*/

    /*
     * Function:_createMatrixEqation
     * Access Level: Private
     * Parameters: none
     * Description:Creates a Matrix Determinent equation.
     */
    var _createMatrixEquation = function(){
        _matrix = KA.Matrix.createMatrix(_row, _column);
        KA.Matrix.populate(_matrix, _row, _column);
        _matrixEquation = KA.Matrix.createEquation(_matrix, _row, _column);

        _equation = "<div style='font-size:150%'>\\["  + _matrixEquation  + "  =   ?\\]</div>";
        $("#dvQuestion").append(_equation);

        var correctAnswer = (_matrix[0][0] * ((_matrix[1][1] * _matrix[2][2])-(_matrix[1][2] * _matrix[2][1]))) - (_matrix[0][1] * ((_matrix[1][0] * _matrix[2][2])-(_matrix[1][2] * _matrix[2][0]))) + (_matrix[0][2] * ((_matrix[1][0] * _matrix[2][1])-(_matrix[1][1] * _matrix[2][0])))
        setCorrectAnswer(correctAnswer);

        var subMatrix1 = "\\begin{vmatrix}\\mathbf{" + _matrix[1][1]  + "}&\\mathbf{" + _matrix[1][2]  + "}\\\\\\mathbf{" + _matrix[2][1]  + "}&\\mathbf{" + _matrix[2][2]  + "}\\end{vmatrix}"
        var subMatrix2 = "\\begin{vmatrix}\\mathbf{" + _matrix[1][0]  + "}&\\mathbf{" + _matrix[1][2]  + "}\\\\\\mathbf{" + _matrix[2][0]  + "}&\\mathbf{" + _matrix[2][2]  + "}\\end{vmatrix}"
        var subMatrix3 = "\\begin{vmatrix}\\mathbf{" + _matrix[1][0]  + "}&\\mathbf{" + _matrix[1][1]  + "}\\\\\\mathbf{" + _matrix[2][0]  + "}&\\mathbf{" + _matrix[2][1]  + "}\\end{vmatrix}"

        $("#dvHint").append("<div><div style='float:left; font-size:150%; color:Red;'>\\[" + _matrix[0][0] + "*" + subMatrix1 + "\\]</div> <div id='dvHint2' style='float:left; font-size:150%; padding-left:8px; color:Blue; display:none;'>\\[ - " + _matrix[0][1] + "*" + subMatrix2 +  "\\]</div> <div id='dvHint3' style='float:left; font-size:150%; padding-left:8px; color:Green; display:none;' >\\[ + " + _matrix[0][2] + "*" + subMatrix3 + "\\]</div> </div>");
        $("#dvHint_simplified1").append("<div><div style='float:left; font-size:150%; color:Red;'>\\[" + _matrix[0][0] + "*(" + _matrix[1][1] + "*" + _matrix[2][2] + " - " + _matrix[1][2] + "*" + _matrix[2][1] + ")\\]</div> <div style='float:left; font-size:150%; padding-left:8px; color:Blue;'>\\[ - " + _matrix[0][1] + "*(" + _matrix[1][0] + "*" + _matrix[2][2] + " - " + _matrix[1][2] + "*" + _matrix[2][0] + ")\\]</div> <div style='float:left; font-size:150%; padding-left:8px; color:Green;'>\\[ + " + _matrix[0][2] + "*(" + _matrix[1][0] + "*" + _matrix[2][1] + " - " + _matrix[1][1] + "*" + _matrix[2][0] + ")\\]</div> </div>");
        $("#dvHint_simplified2").append("<div><div style='float:left; font-size:150%; color:Red;'>\\[" + _matrix[0][0] + "*(" +(( _matrix[1][1] * _matrix[2][2]) - (_matrix[1][2] * _matrix[2][1])) + ")\\]</div> <div style='float:left; font-size:150%; padding-left:8px; color:Blue;'>\\[ - " + _matrix[0][1] + "*(" + ((_matrix[1][0] * _matrix[2][2]) - (_matrix[1][2] * _matrix[2][0])) + ")\\]</div> <div style='float:left; font-size:150%; padding-left:8px; color:Green;'>\\[ + " + _matrix[0][2] + "*(" + ((_matrix[1][0] * _matrix[2][1]) - (_matrix[1][1] * _matrix[2][0])) + ")\\]</div> </div>");
        $("#dvHint_simplified3").append("<div><div style='float:left; font-size:150%; color:Red;'>\\[" + (_matrix[0][0] *(( _matrix[1][1] * _matrix[2][2]) - (_matrix[1][2] * _matrix[2][1]))) + "\\]</div> <div style='float:left; font-size:150%; padding-left:8px; color:Blue;'>\\[ "+ ((((_matrix[1][0] * _matrix[2][2]) - (_matrix[1][2] * _matrix[2][0]))<0)? (" + " + ((-1)*(_matrix[0][1] * ((_matrix[1][0] * _matrix[2][2]) - (_matrix[1][2] * _matrix[2][0]))))): ("-" + ((_matrix[0][1] * ((_matrix[1][0] * _matrix[2][2]) - (_matrix[1][2] * _matrix[2][0]))))))  + "\\]</div> <div style='float:left; font-size:150%; padding-left:8px; color:Green;'>\\[ " + (((_matrix[1][0] * _matrix[2][1]) - (_matrix[1][1] * _matrix[2][0]))<0?"":"+") + (_matrix[0][2] * ((_matrix[1][0] * _matrix[2][1]) - (_matrix[1][1] * _matrix[2][0]))) + " = " + correctAnswer + "\\]</div> </div>");
        $("#dvSample3x3").append("\\[det(A) = \\begin{vmatrix}\\mathbf{a}&\\mathbf{b}&\\mathbf{c}\\\\\\mathbf{d}&\\mathbf{e}&\\mathbf{f}\\\\\\mathbf{g}&\\mathbf{h}&\\mathbf{i}\\end{vmatrix} = ?\\]");
        $("#dvSample3x3").append("\\[det(A) = a\\begin{vmatrix}\\mathbf{e}&\\mathbf{f}\\\\\\mathbf{h}&\\mathbf{i}\\end{vmatrix} - b\\begin{vmatrix}\\mathbf{d}&\\mathbf{f}\\\\\\mathbf{g}&\\mathbf{i}\\end{vmatrix} + c\\begin{vmatrix}\\mathbf{d}&\\mathbf{e}\\\\\\mathbf{g}&\\mathbf{h}\\end{vmatrix}\\]");
        $("#dvSample3x3").append("\\[det(A) = a(e*i - f*h) - b(d*i - f*g) + c(d*h - e*g)\\]");
    }
    var _changeMatrixElementColor = function(elementNumber, color){
        $("#dvQuestion .mfenced:eq(0) span .mn:eq(" + elementNumber  + ")").css("color",color);
    }
    return {
        /*Public Methods*/

        /*
        * Access Level: Public
        * Function: init
        * Parameters: none
        * Detail: Initialize Matrix Determinent Exercise
        */
        init: function(){
            _createMatrixEquation();
        },


        /*
        * Access Level: Private
        * Function: next_step
        * Parameters: none
        * Detail: Create next hint step for user.
        */
        next_step: function(){
            _hintsGiven++;
            steps_given++;
            if(_hintsGiven == 1){
                $("#dvSample3x3").css("display","");
            } else if(_hintsGiven == 2){
                $("#dvHint").css("display","");
                _changeMatrixElementColor(0,"Red");
                _changeMatrixElementColor(4,"Red");
                _changeMatrixElementColor(5,"Red");
                _changeMatrixElementColor(7,"Red");
                _changeMatrixElementColor(8,"Red");
            } else if(_hintsGiven == 3){
                $("#dvHint2").css("display","");
                $("#dvHintText").css("color","Red");
                $("#dvQuestion .mfenced:eq(0) span .mn").css("color","Black");
                _changeMatrixElementColor(1,"Blue");
                _changeMatrixElementColor(2,"Blue");
                _changeMatrixElementColor(3,"Blue");
                _changeMatrixElementColor(7,"Blue");
                _changeMatrixElementColor(8,"Blue");
            } else if(_hintsGiven == 4){
                $("#dvHint3").css("display","");
                $("#dvHintText").css("color","Red");
                $("#dvQuestion .mfenced:eq(0) span .mn").css("color","Black");
                _changeMatrixElementColor(1,"Green");
                _changeMatrixElementColor(2,"Green");
                _changeMatrixElementColor(4,"Green");
                _changeMatrixElementColor(5,"Green");
                _changeMatrixElementColor(6,"Green");
            } else if(_hintsGiven == 5){
                $("#dvQuestion .mfenced:eq(0) span .mn").css("color","Black");
                $("#dvHint_simplified1").css("display","");
            } else if(_hintsGiven == 6){
                $("#dvHint_simplified2").css("display","");
            } else if(_hintsGiven == 7){
                $("#dvHint_simplified3").css("display","");
            }
        }
    };
};


$(document).ready(function(){
    Matrix.Determinant.init();
})