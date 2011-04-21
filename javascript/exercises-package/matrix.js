/*
* Author: Gohar-UL-Islam
* Date: 25 March 2011
* Description: Matrix Class With General Functions.
*/

if (typeof KA == "undefined") {
    KA = function() { };
}

KA.Matrix = new function(){
    var _matrix = null;
    var _matrixEquation = "";

    return{
        
        /*
        * Access Level: Public
        * Function: createMatrix
        * Parameters1 Name: MatrixRows
        * Parameters1 Type: integer
        * Parameters1 Description: Number of rows of matrix.
        *
        * Parameters2 Name: MatrixColumns
        * Parameters2 Type: integer
        * Parameters2 Description: Number of columns of matrix.
        * 
        * Detail: Initialize Matrix Multiplication Exercise
        */
        createMatrix: function(MatrixRows, MatrixColumns){
            var _matrix = new Array(MatrixRows);
            for(var loopI=0; loopI < MatrixRows; loopI++){
                _matrix[loopI] = new Array(MatrixColumns);
            }
            return _matrix;
        },


        /*
        * Access Level: Public
        * Function: populate
        * Parameters1 Name: Matrix
        * Parameters1 Type: 2 dimensional array
        * Parameters1 Description: Matrix to be populated.
        *
        * Parameters2 Name: MatrixRows
        * Parameters2 Type: integer
        * Parameters2 Description: Number of rows of matrix.
        *
        * Parameters3 Name: MatrixColumns
        * Parameters3 Type: integer
        * Parameters3 Description: Number of columns of matrix.
        * Function Detail: Populate 2 dimensional array for matrix creation wirh random numbers
        */
        populate: function(Matrix, MatrixRows, MatrixColumns){
            for(var loopI=0; loopI < MatrixRows; loopI++){
                for(var loopJ=0; loopJ < MatrixColumns; loopJ++){
                    Matrix[loopI][loopJ] = Math.abs(get_random());
                }
            }          
            return _matrixEquation;
        },


        /*
        * Access Level: Public
        * Function: add
        * Parameters1 Name: LeftMatrix
        * Parameters1 Type: 2 dimensional array
        * Parameters1 Description: Matrix 1 to add.
        *
        * Parameters1 Name: RightMatrix
        * Parameters1 Type: 2 dimensional array
        * Parameters1 Description: Matrix 2 to add.
        *
        * Parameters2 Name: Rows
        * Parameters2 Type: integer
        * Parameters2 Description: Number of rows of matrix.
        *
        * Parameters3 Name: Columns
        * Parameters3 Type: integer
        * Parameters3 Description: Number of columns of matrix.
        *
        * Parameters1 Name: ResultentMatrix
        * Parameters1 Type: 2 dimensional array
        * Parameters1 Description: 2 dimensional array to store the result of sum of matrices.
        *
        * Function Detail: add the provided matrices and store the result in resultent matrix.
        */
        add: function(LeftMatrix, RightMatrix, Rows, Columns, ResultentMatrix){
            for(var loopI=0; loopI < Rows; loopI++)
            {
                for(var loopJ=0; loopJ < Columns; loopJ++)
                {
                    ResultentMatrix[loopI][loopJ] = LeftMatrix[loopI][loopJ] + RightMatrix[loopI][loopJ];
                }
            }
            
        },


        /*
        * Access Level: Public
        * Function: subtract
        * Parameters1 Name: LeftMatrix
        * Parameters1 Type: 2 dimensional array
        * Parameters1 Description: Matrix 1 to add.
        *
        * Parameters1 Name: RightMatrix
        * Parameters1 Type: 2 dimensional array
        * Parameters1 Description: Matrix 2 to add.
        *
        * Parameters2 Name: Rows
        * Parameters2 Type: integer
        * Parameters2 Description: Number of rows of matrix.
        *
        * Parameters3 Name: Columns
        * Parameters3 Type: integer
        * Parameters3 Description: Number of columns of matrix.
        *
        * Parameters1 Name: ResultentMatrix
        * Parameters1 Type: 2 dimensional array
        * Parameters1 Description: 2 dimensional array to store the result of difference of matrices.
        *
        * Function Detail: Subtract the provided matrices and store the result in resultent matrix.
        */
        subtract: function(LeftMatrix, RightMatrix, Rows, Columns, ResultentMatrix, DoSwapGreaterValue){
            for(var loopI=0; loopI < Rows; loopI++)
            {
                for(var loopJ=0; loopJ < Columns; loopJ++){
                    if((RightMatrix[loopI][loopJ] > LeftMatrix[loopI][loopJ]) && DoSwapGreaterValue == true ){
                        RightMatrix[loopI][loopJ] = RightMatrix[loopI][loopJ] + LeftMatrix[loopI][loopJ];
                        LeftMatrix[loopI][loopJ] = RightMatrix[loopI][loopJ] - LeftMatrix[loopI][loopJ];
                        RightMatrix[loopI][loopJ] = RightMatrix[loopI][loopJ] - LeftMatrix[loopI][loopJ];
                    }
                    ResultentMatrix[loopI][loopJ] = LeftMatrix[loopI][loopJ] - RightMatrix[loopI][loopJ];
                }
            }
        },


        /*
        * Access Level: Public
        * Function: createEquation
        * Parameters1 Name: Matrix
        * Parameters1 Type: 2 dimensional array
        * Parameters1 Description: Matrix for which LaTeX need to be generated.
        *
        * Parameters2 Name: MatrixRows
        * Parameters2 Type: integer
        * Parameters2 Description: Number of rows of matrix.
        *
        * Parameters3 Name: MatrixColumns
        * Parameters3 Type: integer
        * Parameters3 Description: Number of columns of matrix.
        * Function Detail: Crdeate LaTex string for provided matrix
        * Return Type: String
        * Return: LaTex String
        */
        createEquation: function(Matrix, MatrixRows, MatrixColumns){
            _matrixEquation = "\\begin{bmatrix}";
            for(var loopI=0; loopI < MatrixRows; loopI++){
                _matrixEquation +=  "\\\\";
                for(var loopJ=0; loopJ < MatrixColumns; loopJ++){
                    if(loopJ==0){
                        _matrixEquation += "\\mathbf{" + Matrix[loopI][loopJ]  + "}";
                    } else {
                        _matrixEquation += "& \\mathbf{" + Matrix[loopI][loopJ]  + "}";
                    }
                }
            }
            _matrixEquation += "\\end{bmatrix}";

            return _matrixEquation;
        },


        /*
        * Access Level: Public
        * Function: multiply
        * Parameters1 Name: LeftMatrix
        * Parameters1 Type: 2 dimensional array
        * Parameters1 Description: Matrix 1 to multiply.
        *
        * Parameters2 Name: LeftMatrixRows
        * Parameters2 Type: integer
        * Parameters2 Description: Number of rows of matrix 1.
        *
        * Parameters3 Name: LeftMatrixColumns
        * Parameters3 Type: integer
        * Parameters3 Description: Number of columns of matrix 1.
        *
        * Parameters1 Name: RightMatrix
        * Parameters1 Type: 2 dimensional array
        * Parameters1 Description: Matrix 2 to multiply.
        *
        * Parameters3 Name: RightMatrixColumns
        * Parameters3 Type: integer
        * Parameters3 Description: Number of columns of matrix.
        *
        * Parameters1 Name: ResultentMatrix
        * Parameters1 Type: 2 dimensional array
        * Parameters1 Description: 2 dimensional array to store the result of product of matrices.
        *
        * Function Detail: multiply the provided matrices and store the result in resultent matrix.
        */
        multiply: function(LeftMatrix, LeftMatrixRows, LeftMatrixColumns, RightMatrix, RightMatrixColumns, ResultentMatrix){
            for(var loopI=0; loopI < LeftMatrixRows; loopI++){
                for(var loopJ=0; loopJ < LeftMatrixColumns; loopJ++){
                    for(var loopK=0; loopK < RightMatrixColumns; loopK++){
                        if(ResultentMatrix[loopI][loopK] != null){
                            ResultentMatrix[loopI][loopK] +=  LeftMatrix[loopI][loopJ] * RightMatrix[loopJ][loopK];
                        } else {
                            ResultentMatrix[loopI][loopK] = LeftMatrix[loopI][loopJ] * RightMatrix[loopJ][loopK];
                        }
                    }
                }
            }
        },


       /*
        * Access Level: Public
        * Function: answerHtml
        *
        * Parameters1 Name: rows
        * Parameters1 Type: integer
        * Parameters1 Description: Number of rows of of answer textboxes.
        *
        * Parameters2 Name: column
        * Parameters2 Type: integer
        * Parameters2 Description: Number of columns of of answer textboxes.
        *
        */
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