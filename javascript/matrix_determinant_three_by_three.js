/*
* Author: Gohar-UL-Islam
* Date: 20 Feb 2011
* Description: Fraction determinent exercise.
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
                    MathJax.Message.Set("Can't load web font TeX/"+font.directory,null,500);
                    document.getElementById("noWebFont").style.display = "";
                },
                firefoxFontError: function (font) {
                    MathJax.Message.Set("Firefox can't load web fonts from a remote host",null,500);
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
    var _createMatrixEqation = function(){

        var loopI =0;
        var loopJ =0;

        _matrix = new Array(_row);

        for(loopI=0; loopI < _row; loopI++)
        {
            _matrix[loopI] = new Array(_column);
        }

        _matrixEquation = "\\begin{vmatrix}";

        for(loopI=0; loopI < _row; loopI++)
        {
            if(loopI != 0){
                _matrixEquation = _matrixEquation +  "\\\\";
            }
            for(loopJ=0; loopJ < _column; loopJ++)
            {
                _matrix[loopI][loopJ] = Math.abs(get_random());
                if(loopJ == 0){
                    _matrixEquation = _matrixEquation + "\\mathbf{" + _matrix[loopI][loopJ]  + "}";
                } else {
                    _matrixEquation = _matrixEquation + " & \\mathbf{" + _matrix[loopI][loopJ]  + "}";
                }
            }
        }
        _matrixEquation = _matrixEquation + "\\end{vmatrix}";

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
        $("#dvSample3x3").append("\\[det(A) = a\\begin{vmatrix}\\mathbf{e}&\\mathbf{f}\\\\\\mathbf{h}&\\mathbf{i}\\end{vmatrix} - b\\begin{vmatrix}\\mathbf{d}&\\mathbf{f}\\\\\\mathbf{g}&\\mathbf{i}\\end{vmatrix} + c\\begin{vmatrix}\\mathbf{d}&\\mathbf{e}\\\\\\mathbf{g}&\\mathbf{h}\\end{vmatrix}\\]")
        $("#dvSample3x3").append("\\[det(A) = a(e*i - f*h) - b(d*i - f*g) + c(d*h - e*g)\\]")

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
            _createMatrixEqation();
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
                $("#dvQuestion .mfenced:eq(0) span .mn:eq(0)").css("color","Red");
                $("#dvQuestion .mfenced:eq(0) span .mn:eq(4)").css("color","Red");
                $("#dvQuestion .mfenced:eq(0) span .mn:eq(5)").css("color","Red");
                $("#dvQuestion .mfenced:eq(0) span .mn:eq(7)").css("color","Red");
                $("#dvQuestion .mfenced:eq(0) span .mn:eq(8)").css("color","Red");
            } else if(_hintsGiven == 3){
                $("#dvHint2").css("display","");
                $("#dvHintText").css("color","Red");
                $("#dvQuestion .mfenced:eq(0) span .mn").css("color","Black");
                $("#dvQuestion .mfenced:eq(0) span .mn:eq(1)").css("color","Blue");
                $("#dvQuestion .mfenced:eq(0) span .mn:eq(2)").css("color","Blue");
                $("#dvQuestion .mfenced:eq(0) span .mn:eq(3)").css("color","Blue");
                $("#dvQuestion .mfenced:eq(0) span .mn:eq(7)").css("color","Blue");
                $("#dvQuestion .mfenced:eq(0) span .mn:eq(8)").css("color","Blue");
            } else if(_hintsGiven == 4){
                $("#dvHint3").css("display","");
                $("#dvHintText").css("color","Red");
                $("#dvQuestion .mfenced:eq(0) span .mn").css("color","Black");
                $("#dvQuestion .mfenced:eq(0) span .mn:eq(1)").css("color","Green");
                $("#dvQuestion .mfenced:eq(0) span .mn:eq(2)").css("color","Green");
                $("#dvQuestion .mfenced:eq(0) span .mn:eq(4)").css("color","Green");
                $("#dvQuestion .mfenced:eq(0) span .mn:eq(5)").css("color","Green");
                $("#dvQuestion .mfenced:eq(0) span .mn:eq(6)").css("color","Green");
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