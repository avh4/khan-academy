// Scaling vectors
// Author: Marcia Lee
// Date: 2011-04-23
//
// Video spec:
//  http://vimeo.com/22676123
// Problem speclet:
//

function ScalingVectorsExercise() {
    // 0th index is starting vector
    // correct answer is randomly assigned to 1-4th indices.
    var vectors = [];
    var coeff;
    var correct_index;
    
    generateProblem();
    showProblem();
    generateHints();
            
    function generateProblem() {
        var num_vectors = 5;
        coeff = getRandomIntRange(2, 3) * (getRandomIntRange(0, 1) ? 1 : -1);
        while(vectors.length < num_vectors) {
            if (vectors.length == 0)
                var v = generateVector(-3, 3, -3, 3);
            else
                var v = generateVector(-9, 9, -9, 9);
            addVectorToProblem(v);
        }
        
        // throw in -1 * the correct answer
        var vector = vectors[getRandomIntRange(1, num_vectors - 1)]
        vector.x = -1 * coeff * vectors[0].x;
        vector.y = -1 * coeff * vectors[0].y;
        
        correct_index = getRandomIntRange(1, num_vectors - 1);
        var correct = vectors[correct_index];
        correct.x = coeff * vectors[0].x;
        correct.y = coeff * vectors[0].y;
        
        write_text("Which of these is equal to " + "`" + coeff + "\\vec{" + vectors[0].name + "}" + "`" + "?");
        setCorrectAnswer("\\vec{" + vectors[correct_index].name + "}");
        for (var i = 1; i < num_vectors; i++) {
            addWrongChoice("\\vec{" +vectors[i].name + "}");
        }
    }
    
    function showProblem() {
        RaphaelWrapper.drawPlane(-12, 12, -12, 12);
        present.fontsize = "15";
        present.fontfamily = "sans-serif";
        present.fontstyle = "bold";
        present.marker = "arrow";
        
        for (var i = 0; i < vectors.length; i++) {
            drawVector(vectors[i], i);
        }
    }
    
    function generateHints() {
        write_step("`" + "\\vec{" + vectors[0].name + "}" + " = " + outputVector(vectors[0]) 
                    + "= (" + vectors[0].x + "," + vectors[0].y + ")"
                    + "= ` \\(\\begin{bmatrix}" + vectors[0].x + "\\\\" + vectors[0].y + "\\\\ \\end{bmatrix}\\)");
        write_step("There are two ways to approach this problem.");
        write_step("1) Multiply the `" + i_hat + "` and `" + j_hat + "` components" + " by " + coeff + ".");
        write_step("`" + coeff + "\\vec{" + vectors[0].name + "}"
                    + " = (" + coeff + " * " + vectors[0].x + " ) " + i_hat + " + ( " + coeff + " * " + vectors[0].y + ")" + j_hat); 
        write_step("` = " + outputVector(vectors[correct_index]) + "`");
        write_step("` = \\vec{" + vectors[correct_index].name + "} `");
        write_step("2) Solve this graphically.");
    }
    
    function generateVector(min_x, max_x, min_y, max_y) {
        min_x = Math.min(min_x, max_x);
        max_x = Math.max(min_x, max_x);
        min_y = Math.min(min_y, max_y);
        max_y = Math.max(min_y, max_y);

        var x_val = 0;
        var y_val = 0;
        
        while (!x_val && !y_val) {
            x_val = getRandomIntRange(min_x, max_x);
            y_val = getRandomIntRange(min_y, max_y);
        }
        return {x: x_val, y: y_val};
    }
    
    function addVectorToProblem(v) {
        var start_code = "a".charCodeAt(0);
        if (indexOf(vectors, v) == -1) {
            v.color = (vectors.length ? getNextColor() : "red");
            v.name = String.fromCharCode(start_code + vectors.length);
            vectors[vectors.length] = v;
        }
    }
    
    function drawVector(vector, quadrant) {
        present.stroke = vector.color;

        switch(quadrant % 4) {
            case 0:
                var min_x = Math.max(1, 1 - vector.x);
                var max_x = Math.min(9, 9 - vector.x);
                var min_y = Math.max(1, 1 - vector.y);
                var max_y = Math.min(9, 9 - vector.y);
                break;
            case 1:
                var min_x = Math.max(-9, -9 - vector.x);
                var max_x = Math.min(-1, -1 - vector.x);
                var min_y = Math.max(1, 1 - vector.y);
                var max_y = Math.min(9, 9 - vector.y);
                break;
            case 2:
                var min_x = Math.max(-9, -9 - vector.x);
                var max_x = Math.min(-1, -1 - vector.x);
                var min_y = Math.max(-9, -9 - vector.y);
                var max_y = Math.min(-1, -1 - vector.y);
                break;
            default:
                var min_x = Math.max(1, 1 - vector.x);
                var max_x = Math.min(9, 9 - vector.x);
                var min_y = Math.max(-9, -9 - vector.y);
                var max_y = Math.min(-1, -1 - vector.y);
                break;
        }
        
        var offset = generateVector(min_x, max_x, min_y, max_y);
        vector.offset = offset;
        
        var offset_coord = [offset.x, offset.y];
        var vector_coord = [vector.x + offset.x, vector.y + offset.y];
        present.line(offset_coord, vector_coord);
        present.text(vector_coord, vector.name);
    }
        
    function drawComponents(v) {
        var offset_x = v.offset.x;
        var offset_y = v.offset.y
        var offset_coord = [offset_x, offset_y];
        var x_coord = offset_coord.slice();
        x_coord[0] += v.x;

        var y_coord = x_coord.slice();
        y_coord[1] += v.y;
        present.stroke = "blue";       
        present.line(offset_coord, x_coord);
        present.stroke = "green";
        present.line(x_coord, y_coord);
    }
    
    this.showGraphHints = function(hint_num) {
        present.marker = "none";
        present.strokewidth = "3";
        if (hint_num == 0)
            drawComponents(vectors[0]);
        if (hint_num == 6)
            drawComponents(vectors[correct_index]);
    }
}
