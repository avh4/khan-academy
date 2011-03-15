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
                    MathJax.Message.Set("Can't load web font TeX/"+font.directory,null,2000);
                    document.getElementById("noWebFont").style.display = "";
                },
                firefoxFontError: function (font) {
                    MathJax.Message.Set("Firefox can't load web fonts from a remote host",null,2000);
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
Matrix.Determinent = new function(){

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

        _equation = "<div style='font-size:250%'>\\["  + _matrixEquation  + "  =   ?\\]</div>";
        $("#dvQuestion").append(_equation);
        var correctAnswer = (_matrix[0][0] * ((_matrix[1][1] * _matrix[2][2])-(_matrix[1][2] * _matrix[2][1]))) - (_matrix[0][1] * ((_matrix[1][0] * _matrix[2][2])-(_matrix[1][2] * _matrix[2][0]))) + (_matrix[0][2] * ((_matrix[1][0] * _matrix[2][1])-(_matrix[1][1] * _matrix[2][0])))
        setCorrectAnswer(correctAnswer);

        var subMatrix1 = "\\begin{vmatrix}\\mathbf{" + _matrix[1][1]  + "}&\\mathbf{" + _matrix[1][2]  + "}\\\\\\mathbf{" + _matrix[2][1]  + "}&\\mathbf{" + _matrix[2][2]  + "}\\end{vmatrix}"
        var subMatrix2 = "\\begin{vmatrix}\\mathbf{" + _matrix[1][0]  + "}&\\mathbf{" + _matrix[1][2]  + "}\\\\\\mathbf{" + _matrix[2][0]  + "}&\\mathbf{" + _matrix[2][2]  + "}\\end{vmatrix}"
        var subMatrix3 = "\\begin{vmatrix}\\mathbf{" + _matrix[1][0]  + "}&\\mathbf{" + _matrix[1][1]  + "}\\\\\\mathbf{" + _matrix[2][0]  + "}&\\mathbf{" + _matrix[2][1]  + "}\\end{vmatrix}"
        $("#dvHint").append("<div><div style='float:left; font-size:150%; color:Red;'>\\[" + _matrix[0][0] + "*" + subMatrix1 + "\\]</div> <div id='dvHint2' style='float:left; font-size:150%; padding-left:8px; color:Blue; display:none;'>\\[ - " + _matrix[0][1] + "*" + subMatrix2 +  "\\]</div> <div id='dvHint3' style='float:left; font-size:150%; padding-left:8px; color:Green; display:none;' >\\[ + " + _matrix[0][2] + "*" + subMatrix3 + "\\]</div> </div>");
        $("#dvHint_simplified1").append("<div><div style='float:left; font-size:150%; color:Red;'>\\[" + _matrix[0][0] + "*(" + _matrix[1][1] + "*" + _matrix[2][2] + " - " + _matrix[1][2] + "*" + _matrix[2][1] + ")\\]</div> <div style='float:left; font-size:150%; padding-left:8px; color:Blue;'>\\[ - " + _matrix[0][1] + "*(" + _matrix[1][0] + "*" + _matrix[2][2] + " - " + _matrix[1][2] + "*" + _matrix[2][0] + ")\\]</div> <div style='float:left; font-size:150%; padding-left:8px; color:Green;'>\\[ + " + _matrix[0][2] + "*(" + _matrix[1][0] + "*" + _matrix[2][1] + " - " + _matrix[1][1] + "*" + _matrix[2][0] + ")\\]</div> </div>");
        $("#dvHint_simplified2").append("<div><div style='float:left; font-size:150%; color:Red;'>\\[" + _matrix[0][0] + "*(" +(( _matrix[1][1] * _matrix[2][2]) - (_matrix[1][2] * _matrix[2][1])) + ")\\]</div> <div style='float:left; font-size:150%; padding-left:8px; color:Blue;'>\\[ - " + _matrix[0][1] + "*(" + ((_matrix[1][0] * _matrix[2][2]) - (_matrix[1][2] * _matrix[2][0])) + ")\\]</div> <div style='float:left; font-size:150%; padding-left:8px; color:Green;'>\\[ + " + _matrix[0][2] + "*(" + ((_matrix[1][0] * _matrix[2][1]) - (_matrix[1][1] * _matrix[2][0])) + ")\\]</div> </div>");
        $("#dvHint_simplified3").append("<div><div style='float:left; font-size:150%; color:Red;'>\\[" + (_matrix[0][0] *(( _matrix[1][1] * _matrix[2][2]) - (_matrix[1][2] * _matrix[2][1]))) + "\\]</div> <div style='float:left; font-size:150%; padding-left:8px; color:Blue;'>\\[ "+ ((((_matrix[1][0] * _matrix[2][2]) - (_matrix[1][2] * _matrix[2][0]))<0)? " + ": "-") + ((-1)*(_matrix[0][1] * ((_matrix[1][0] * _matrix[2][2]) - (_matrix[1][2] * _matrix[2][0])))) + "\\]</div> <div style='float:left; font-size:150%; padding-left:8px; color:Green;'>\\[ " + (((_matrix[1][0] * _matrix[2][1]) - (_matrix[1][1] * _matrix[2][0]))<0?"":"+") + (_matrix[0][2] * ((_matrix[1][0] * _matrix[2][1]) - (_matrix[1][1] * _matrix[2][0]))) + " = " + correctAnswer + "\\]</div> </div>");
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
                $("#dvHint").css("display","");


                $("#dvQuestion .mfenced:eq(0) span .mn:eq(0)").animate( {
                    color: "Red"
                }, 2000);
                $("#dvQuestion .mfenced:eq(0) span .mn:eq(1)").animate( {
                    color: "#DFDFDF"
                }, 2000);
                $("#dvQuestion .mfenced:eq(0) span .mn:eq(2)").animate( {
                    color: "#DFDFDF"
                }, 2000);
                $("#dvQuestion .mfenced:eq(0) span .mn:eq(3)").animate( {
                    color: "#DFDFDF"
                }, 2000);
                $("#dvQuestion .mfenced:eq(0) span .mn:eq(6)").animate( {
                    color: "#DFDFDF"
                }, 2000);
                $("#dvQuestion .mfenced:eq(0) span .mn:eq(4)").animate( {
                    color: "Red"
                }, 2000);
                $("#dvQuestion .mfenced:eq(0) span .mn:eq(5)").animate( {
                    color: "Red"
                }, 2000);
                $("#dvQuestion .mfenced:eq(0) span .mn:eq(7)").animate( {
                    color: "Red"
                }, 2000);
                $("#dvQuestion .mfenced:eq(0) span .mn:eq(8)").animate( {
                    color: "Red"
                }, 2000);

             
            } else if(_hintsGiven == 2){
                $("#dvHint2").css("display","");

                $("#dvHintText").css("color","Red");

                $("#dvQuestion .mfenced:eq(0) span .mn").animate( {
                    color: "Black"
                }, 100);

                $("#dvQuestion .mfenced:eq(0) span .mn:eq(0)").animate( {
                    color: "#DFDFDF"
                }, 2000);
                $("#dvQuestion .mfenced:eq(0) span .mn:eq(1)").animate( {
                    color: "Blue"
                }, 2000);
                $("#dvQuestion .mfenced:eq(0) span .mn:eq(2)").animate( {
                    color: "Blue"
                }, 2000);

                $("#dvQuestion .mfenced:eq(0) span .mn:eq(3)").animate( {
                    color: "Blue"
                }, 2000);
                $("#dvQuestion .mfenced:eq(0) span .mn:eq(4)").animate( {
                    color: "#DFDFDF"
                }, 2000);
                $("#dvQuestion .mfenced:eq(0) span .mn:eq(5)").animate( {
                    color: "#DFDFDF"
                }, 2000);

                $("#dvQuestion .mfenced:eq(0) span .mn:eq(6)").animate( {
                    color: "#DFDFDF"
                }, 2000);
                $("#dvQuestion .mfenced:eq(0) span .mn:eq(7)").animate( {
                    color: "Blue"
                }, 2000);
                $("#dvQuestion .mfenced:eq(0) span .mn:eq(8)").animate( {
                    color: "Blue"
                }, 2000);

             
                

            } else if(_hintsGiven == 3){
                $("#dvHint3").css("display","");

                $("#dvHintText").css("color","Red");
                $("#dvQuestion .mfenced:eq(0) span .mn").animate( {
                    color: "Black"
                }, 100);

                $("#dvQuestion .mfenced:eq(0) span .mn:eq(0)").animate( {
                    color: "#DFDFDF"
                }, 2000);
                $("#dvQuestion .mfenced:eq(0) span .mn:eq(1)").animate( {
                    color: "Green"
                }, 2000);
                $("#dvQuestion .mfenced:eq(0) span .mn:eq(2)").animate( {
                    color: "Green"
                }, 2000);

                $("#dvQuestion .mfenced:eq(0) span .mn:eq(3)").animate( {
                    color: "#DFDFDF"
                }, 2000);
                $("#dvQuestion .mfenced:eq(0) span .mn:eq(4)").animate( {
                    color: "Green"
                }, 2000);
                $("#dvQuestion .mfenced:eq(0) span .mn:eq(5)").animate( {
                    color: "Green"
                }, 2000);

                $("#dvQuestion .mfenced:eq(0) span .mn:eq(6)").animate( {
                    color: "Green"
                }, 2000);
                $("#dvQuestion .mfenced:eq(0) span .mn:eq(7)").animate( {
                    color: "#DFDFDF"
                }, 2000);
                $("#dvQuestion .mfenced:eq(0) span .mn:eq(8)").animate( {
                    color: "#DFDFDF"
                }, 2000);

            } else if(_hintsGiven == 4){
                $("#dvQuestion .mfenced:eq(0) span .mn").animate( {
                    color: "Black"
                }, 100);
                $("#dvHint_simplified1").css("display","");
            } else if(_hintsGiven == 5){
                $("#dvHint_simplified2").css("display","");
            } else if(_hintsGiven == 6){
                $("#dvHint_simplified3").css("display","");
            }
        }
    };
};


$(document).ready(function(){
    Matrix.Determinent.init();
})