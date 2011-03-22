/*
* Author: Gohar-UL-Islam
* Date: 20 Feb 2011
* Description: Matrix Multiplication exercise.
*/


/*
 * Confiure LaTeX
 */
MathJax.HTML.Cookie.Set("menu",{});
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

    var _wrongChoices = new Array();

    /*Private Methods*/

    /*
     * Function:_createMatrixEqation
     * Access Level: Private
     * Parameters: none
     * Description:Creates a Matrix Multiplication equation with common dinominators
     */
    var _createMatrixEquation = function(){
        var _wrongMatrixEquation1 = null;
        var _wrongMatrixEquation2 = null;
        var _wrongMatrixEquation3 = null;
        var leftMatrixEquation = null;
        var rightMatrixEquation = null;
        var loopI = 0;
        var loopJ = 0;
        var loopK = 0;
        
        _LeftMatrixRow =  Math.abs(get_randomInRange(2,4,0));
        _LeftMatrixColumn =  Math.abs(get_randomInRange(2,4,0));
        _RightMatrixRow = _LeftMatrixColumn;
        _RightMatrixColumn = Math.abs(get_randomInRange(2,4,0));

        _leftMatrix = new Array(_LeftMatrixRow);
        _rightMatrix = new Array(_RightMatrixRow);
        _resultentMatrix = new Array(_LeftMatrixRow);
        _hintMultiplicationArray = new Array(_LeftMatrixColumn);
        for(loopI=0; loopI < _LeftMatrixRow; loopI++)
        {
            _leftMatrix[loopI] = new Array(_LeftMatrixColumn);
            _resultentMatrix[loopI] = new Array(_RightMatrixColumn);
        }
        for(loopI=0; loopI < _RightMatrixRow; loopI++)
        {
            _rightMatrix[loopI] = new Array(_RightMatrixColumn);
        }

        leftMatrixEquation = "\\begin{bmatrix}";
        rightMatrixEquation = "\\begin{bmatrix}";
        _resultMatrixEquation = "\\begin{bmatrix}";

        _wrongMatrixEquation1 = "\\begin{bmatrix}";
        _wrongMatrixEquation2 = "\\begin{bmatrix}";
        _wrongMatrixEquation3 = "\\begin{bmatrix}";

        for(loopI=0; loopI < _LeftMatrixRow; loopI++){
            leftMatrixEquation = leftMatrixEquation +  "\\\\";
            for(loopJ=0; loopJ < _LeftMatrixColumn; loopJ++){
                _leftMatrix[loopI][loopJ] = Math.abs(get_random());
                if(loopJ == 0){
                    leftMatrixEquation = leftMatrixEquation + "\\mathbf{" + _leftMatrix[loopI][loopJ]  + "}";
                } else {
                    leftMatrixEquation = leftMatrixEquation + " & \\mathbf{" + _leftMatrix[loopI][loopJ]  + "}";
                }
            }
        }

        for(loopI=0; loopI < _RightMatrixRow; loopI++){
            rightMatrixEquation = rightMatrixEquation + "\\\\";
            for(loopJ=0; loopJ < _RightMatrixColumn; loopJ++){
                _rightMatrix[loopI][loopJ] = Math.abs(get_random());
                if(loopJ == 0){
                    rightMatrixEquation = rightMatrixEquation + "\\mathbf{" + _rightMatrix[loopI][loopJ]  + "}";
                }else {

                    rightMatrixEquation = rightMatrixEquation + " & \\mathbf{" + _rightMatrix[loopI][loopJ]  + "}";
                }
            }
        }

        for(loopI=0; loopI < _LeftMatrixRow; loopI++){
            for(loopJ=0; loopJ < _LeftMatrixColumn; loopJ++){

                for(loopK=0; loopK < _RightMatrixColumn; loopK++){
                    if(_resultentMatrix[loopI][loopK] != null){
                        _resultentMatrix[loopI][loopK] +=  _leftMatrix[loopI][loopJ] * _rightMatrix[loopJ][loopK];
                    } else {
                        _resultentMatrix[loopI][loopK] = _leftMatrix[loopI][loopJ] * _rightMatrix[loopJ][loopK];
                    }
                }
            }
        }

        for(loopI=0; loopI < _LeftMatrixRow; loopI++)
        {          
            for(loopJ=0; loopJ < _RightMatrixColumn; loopJ++){
                _wrongMatrixEquation1[loopI][loopJ] = Math.abs(get_randomInRange(30,180,0));
                _wrongMatrixEquation2[loopI][loopJ] = Math.abs(get_randomInRange(30,180,0));
                _wrongMatrixEquation3[loopI][loopJ] = Math.abs(get_randomInRange(30,180,0));
            }
        }

        setCorrectAnswer(_resultentMatrix);
        
        for(loopI=0; loopI < _LeftMatrixRow; loopI++)
        {
            _resultMatrixEquation = _resultMatrixEquation + "\\\\";
            _wrongMatrixEquation1 = _wrongMatrixEquation1 + "\\\\";
            _wrongMatrixEquation2 = _wrongMatrixEquation2 + "\\\\";
            _wrongMatrixEquation3 = _wrongMatrixEquation3 + "\\\\";

            for(loopJ=0; loopJ < _RightMatrixColumn; loopJ++){
                if(loopJ == 0){

                    _resultMatrixEquation = _resultMatrixEquation + "\\mathbf{" + _resultentMatrix[loopI][loopJ]  + "}";
                    _wrongMatrixEquation1 = _wrongMatrixEquation1 + "\\mathbf{" +  Math.abs(get_randomInRange(20,180,0))  + "}";
                    _wrongMatrixEquation2 = _wrongMatrixEquation2 + "\\mathbf{" +  Math.abs(get_randomInRange(20,180,0))  + "}";
                    _wrongMatrixEquation3 = _wrongMatrixEquation3 + "\\mathbf{" +  Math.abs(get_randomInRange(20,180,0))  + "}";
                } else {
                    _resultMatrixEquation = _resultMatrixEquation + " & \\mathbf{" + _resultentMatrix[loopI][loopJ]  + "}";
                    _wrongMatrixEquation1 = _wrongMatrixEquation1 + " & \\mathbf{" +  Math.abs(get_randomInRange(20,180,0))  + "}";
                    _wrongMatrixEquation2 = _wrongMatrixEquation2 + " & \\mathbf{" +  Math.abs(get_randomInRange(20,180,0))  + "}";
                    _wrongMatrixEquation3 = _wrongMatrixEquation3 + " & \\mathbf{" +  Math.abs(get_randomInRange(20,180,0))  + "}";
                }
            }
        }

        _wrongMatrixEquation1 = _wrongMatrixEquation1 + "\\end{bmatrix}";
        _wrongChoices.push(_wrongMatrixEquation1);

        _wrongMatrixEquation2 = _wrongMatrixEquation2 + "\\end{bmatrix}";
        _wrongChoices.push(_wrongMatrixEquation2);

        _wrongMatrixEquation3 = _wrongMatrixEquation3 + "\\end{bmatrix}";
        _wrongChoices.push(_wrongMatrixEquation3);

        leftMatrixEquation = leftMatrixEquation + "\\end{bmatrix}";
        rightMatrixEquation = rightMatrixEquation + "\\end{bmatrix}";
        _resultMatrixEquation = _resultMatrixEquation + "\\end{bmatrix}";
                
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
        var tmpTable="";
        var tmpTableRow="";
        tmpTable ="<table cellspacing='0' cellpadding='2'>";
        for (var i=0; i<_LeftMatrixRow; i++){
            tmpTableRow +='<tr>';
            for (var j=0; j<_RightMatrixColumn; j++){
                if(i==0){
                    if(j==0){
                        tmpTableRow += '<td style="border-left:solid 1px black; border-top:solid 1px black;">&nbsp;</td>';
                        tmpTableRow += '<td><input id="txt' + i + '' + j + '" type="text" style="width:25px;" /></td>';

                    } else if(j==_RightMatrixColumn-1){
                        tmpTableRow += '<td><input id="txt' + i + '' + j + '" type="text" style="width:25px;" /></td>';
                        tmpTableRow += '<td style="border-right:solid 1px black; border-top:solid 1px black;">&nbsp;</td>';

                    } else{
                        tmpTableRow += '<td><input id="txt' + i + '' + j + '" type="text" style="width:25px;" /></td>';
                    }
                } else if(i==_LeftMatrixRow-1){
                    if(j==0){
                        tmpTableRow += '<td style="border-left:solid 1px black; border-bottom:solid 1px black;">&nbsp;</td>';
                        tmpTableRow += '<td><input id="txt' + i + '' + j + '" type="text" style="width:25px;" /></td>';
                    } else if(j==_RightMatrixColumn-1){
                        tmpTableRow += '<td><input id="txt' + i + '' + j + '" type="text" style="width:25px;" /></td>';
                        tmpTableRow += '<td style="border-right:solid 1px black; border-bottom:solid 1px black;">&nbsp;</td>';
                    } else{
                        tmpTableRow += '<td><input id="txt' + i + '' + j + '" type="text" style="width:25px;" /></td>';
                    }
                } else {
                    if(j==0){
                        tmpTableRow += '<td style="border-left:solid 1px black;">&nbsp;</td>';
                        tmpTableRow += '<td><input id="txt' + i + '' + j + '" type="text" style="width:25px;" /></td>';
                    } else if(j==_RightMatrixColumn-1){
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