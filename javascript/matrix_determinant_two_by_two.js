/*
* Author: Gohar-UL-Islam
* Date: 20 Feb 2011
* Description: Fraction addition exercise with common dinominators.
*/


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
 * Class Name: Determinent
 */
Matrix.Determinant = new function(){

    /*Private Members*/
    var _hintsGiven = 0;
    var _matrix = null;
    var _matrixEquation = null;
    var _row =  2;
    var _column =  2;
    var _equation = "";
    /*Private Methods*/

    /*
     * Function:_createMatrixEqation
     * Access Level: Private
     * Parameters: none
     * Description:Creates a Matrix determinent equation
     */
    var _createMatrixEquation = function(){

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
        setCorrectAnswer((_matrix[0][0]*_matrix[1][1]) - (_matrix[0][1]*_matrix[1][0]));
        $("#dvHint").append("<div><div style='float:left; font-size:150%'>\\["  + _matrixEquation + "\\]</div> <div style='float:left; font-size:150%; padding-top:18px; padding-left:8px; color:Blue;'>\\[  =  (" + _matrix[0][0] + "*" + _matrix[1][1] + ") \\]</div> <div id='dvHint2' style='float:left; font-size:150%; padding-top:18px; padding-left:8px; display:none;'>\\[ -\\]</div> <div id='dvHint3' style='float:left; font-size:150%; padding-top:18px; padding-left:8px; display:none; color:Red;'>\\[ (" + _matrix[0][1] + "*" + _matrix[1][0] + ") \\]</div> <div id='dvHint4' style='float:left; font-size:150%; padding-top:18px; padding-left:8px; display:none;'>\\[ = " + ((_matrix[0][0]*_matrix[1][1]) - (_matrix[0][1]*_matrix[1][0])) + "  \\]</div></div>");
        $("#dvSample2x2").append("\\[det(A) = \\begin{vmatrix}\\mathbf{a}&\\mathbf{b}\\\\\\mathbf{c}&\\mathbf{d}\\end{vmatrix}=a*d - b*c\\]");
    }
    return {
        /*Public Methods*/

        /*
        * Access Level: Public
        * Function: init
        * Parameters: none
        * Detail: Initialize Matrix determinent Exercise
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
                $("#dvSample2x2").css("display","");
            } else if(_hintsGiven == 2){
                $("#dvHint").css("display","");
                $("#dvHint .mfenced:eq(0) span .mn")[0].style.color="Blue";
                $("#dvHint .mfenced:eq(0) span .mn")[3].style.color="Blue";
                $("#dvHintText").html("Multiplay " + _matrix[0][0] + " with " + _matrix[1][1]);
                $("#dvHintText").css("color","Blue");
            } else if(_hintsGiven == 3){
                $("#dvHint2").css("display","");
                $("#dvHint3").css("display","");
                $("#dvHint .mfenced:eq(0) span .mn")[1].style.color="Red";
                $("#dvHint .mfenced:eq(0) span .mn")[2].style.color="Red";
                $("#dvHintText").html("Subtract the  product of " + _matrix[0][1] + " and " + _matrix[1][0] + ".") ;
                $("#dvHintText").css("color","Red");
            } else if(_hintsGiven == 4){
                $("#dvHint4").css("display","");
            }
        }
    };
};
$(document).ready(function(){
    Matrix.Determinant.init();
})