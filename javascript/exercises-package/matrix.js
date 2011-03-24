if (typeof KA == "undefined") {
    KA = function() { };
}

KA.Matrix = new function(){
    var _matrix = null;
    var _matrixEquation = "";

    return{
        createMatrix: function(pMatrixRows, pMatrixColumns){
            var _matrix = new Array(pMatrixRows);
            for(var loopI=0; loopI < pMatrixRows; loopI++){                
                _matrix[loopI] = new Array(pMatrixColumns);
            }
            return _matrix;
        },
        populate: function(pMatrix, pMatrixRows, pMatrixColumns){
            for(var loopI=0; loopI < pMatrixRows; loopI++){
                for(var loopJ=0; loopJ < pMatrixColumns; loopJ++){
                    pMatrix[loopI][loopJ] = Math.abs(get_random());
                }
            }          
            return _matrixEquation;
        },

        add: function(pLeftMatrix, pRightMatrix, pRows, pColumns, pResultentMatrix){
            for(var loopI=0; loopI < pRows; loopI++)
            {
                for(var loopJ=0; loopJ < pColumns; loopJ++)
                {
                    pResultentMatrix[loopI][loopJ] = pLeftMatrix[loopI][loopJ] + pRightMatrix[loopI][loopJ];
                }
            }
            
        },

        subtract: function(pLeftMatrix, pRightMatrix, pRows, pColumns, pResultentMatrix, pDoSwapGreaterValue){
            for(var loopI=0; loopI < pRows; loopI++)
            {
                for(var loopJ=0; loopJ < pColumns; loopJ++)
                {
                    if((pRightMatrix[loopI][loopJ] > pLeftMatrix[loopI][loopJ]) && pDoSwapGreaterValue == true ){
                        pRightMatrix[loopI][loopJ] = pRightMatrix[loopI][loopJ] + pLeftMatrix[loopI][loopJ];
                        pLeftMatrix[loopI][loopJ] = pRightMatrix[loopI][loopJ] - pLeftMatrix[loopI][loopJ];
                        pRightMatrix[loopI][loopJ] = pRightMatrix[loopI][loopJ] - pLeftMatrix[loopI][loopJ];
                    }
                    pResultentMatrix[loopI][loopJ] = pLeftMatrix[loopI][loopJ] - pRightMatrix[loopI][loopJ];
                }
            }
        },
        
        createEquation: function(pMatrix, pMatrixRows, pMatrixColumns){
            _matrixEquation = "\\begin{bmatrix}";
            for(var loopI=0; loopI < pMatrixRows; loopI++){
                _matrixEquation +=  "\\\\";
                for(var loopJ=0; loopJ < pMatrixColumns; loopJ++){
                    if(loopJ==0){
                        _matrixEquation += "\\mathbf{" + pMatrix[loopI][loopJ]  + "}";
                    } else {
                        _matrixEquation += "& \\mathbf{" + pMatrix[loopI][loopJ]  + "}";
                    }
                }
            }
            _matrixEquation += "\\end{bmatrix}";

            return _matrixEquation;
        },

        
        multiply: function(pLeftMatrix, pLeftMatrixRows, pLeftMatrixColumns, pRightMatrix, pRightMatrixColumns, pResultentMatrix){
            for(var loopI=0; loopI < pLeftMatrixRows; loopI++){
                for(var loopJ=0; loopJ < pLeftMatrixColumns; loopJ++){
                    for(var loopK=0; loopK < pRightMatrixColumns; loopK++){
                        if(pResultentMatrix[loopI][loopK] != null){
                            pResultentMatrix[loopI][loopK] +=  pLeftMatrix[loopI][loopJ] * pRightMatrix[loopJ][loopK];
                        } else {
                            pResultentMatrix[loopI][loopK] = pLeftMatrix[loopI][loopJ] * pRightMatrix[loopJ][loopK];
                        }
                    }
                }
            }
        },
        
        answerHtml: function(row, column){
            var tmpTable ="<table cellspacing='0' cellpadding='2'>";
            var tmpTableRow ="";
            for (var i=0; i<row; i++){
                tmpTableRow +='<tr>';
                for (var j=0; j<column; j++){
                    if(i==0){
                        if(j==0){
                            tmpTableRow += '<td style="border-left:solid 1px black; border-top:solid 1px black;">&nbsp;</td>';
                            tmpTableRow += '<td><input id="txt' + i + '' + j + '" type="text" style="width:25px;" /></td>';

                        } else if(j==column-1){
                            tmpTableRow += '<td><input id="txt' + i + '' + j + '" type="text" style="width:25px;" /></td>';
                            tmpTableRow += '<td style="border-right:solid 1px black; border-top:solid 1px black;">&nbsp;</td>';

                        } else{
                            tmpTableRow += '<td><input id="txt' + i + '' + j + '" type="text" style="width:25px;" /></td>';
                        }
                    } else if(i==row-1){
                        if(j==0){
                            tmpTableRow += '<td style="border-left:solid 1px black; border-bottom:solid 1px black;">&nbsp;</td>';
                            tmpTableRow += '<td><input id="txt' + i + '' + j + '" type="text" style="width:25px;" /></td>';
                        } else if(j==column-1){
                            tmpTableRow += '<td><input id="txt' + i + '' + j + '" type="text" style="width:25px;" /></td>';
                            tmpTableRow += '<td style="border-right:solid 1px black; border-bottom:solid 1px black;">&nbsp;</td>';
                        } else{
                            tmpTableRow += '<td><input id="txt' + i + '' + j + '" type="text" style="width:25px;" /></td>';
                        }
                    } else {
                        if(j==0){
                            tmpTableRow += '<td style="border-left:solid 1px black;">&nbsp;</td>';
                            tmpTableRow += '<td><input id="txt' + i + '' + j + '" type="text" style="width:25px;" /></td>';
                        } else if(j==column-1){
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
            return tmpTable
        }

    }
}