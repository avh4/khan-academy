function RoundingExercise() {
    var number;
    var number_str;
    var rounding_num;
    var num_to_right;
    var answer;
    
    var x_min = 0; 
    var x_max = 400;
    var y_min = 0;
    var y_max = 200;
    var num_line_padding = 20;
    var num_line_y = 150;
    var tick_height = 15;
    
    RoundingType = [{pos: -2, str: "hundredth"},
                    {pos: -1, str: "tenth"},
                    {pos: 0, str: "one"},
                    {pos: 1, str: "ten"},
                    {pos: 2, str: "hundred"},
                    {pos: 3, str: "thousand"}
                    ]
    
    generateProblem();
    showProblem();
    generateHints();

    function generateProblem() {
        var type_index = getRandomIntRange(0, RoundingType.length - 1);
        type = RoundingType[type_index];
        if (type.pos <= 0) {
            number = getRandomIntRange(10, 99);
            var decimal = getRandomIntRange(100, 999);
            number_str = number + "." + decimal;
            number += (decimal / 1000);
            var index = number_str.indexOf(".");
        } else {
            number = getRandomIntRange(1000, 9999);
            number_str = "" + number;
            var index = number_str.length - 1;
        }
        
        rounding_num = number_str[index - type.pos - (type.pos == 0 ? 1 : 0)];
        num_to_right = number_str[index - type.pos + 1];
        
        answer = roundToPosition(number, type.pos);
        setCorrectAnswer(answer);
    }
    
    function showProblem() {
        write_text("Round " + number_str + " to the nearest " + type.str + ".");
    }

    function generateHints() {
        write_step("There are two ways to consider this problem.");
        write_step("The first way is to notice that the digit in the " + type.str + "s place is " + rounding_num
                    + " and that the digit to the right is " + num_to_right + ".");
        if (num_to_right >= 5) {
            write_step("Since the digit to the right (the " + num_to_right + ") is greater than or equal to 5, we should round up to " + answer + ".");
        } else {
            write_step("Since the digit to the right (the " + num_to_right + ") is less than 5, we should round down to " + answer + ".");
        }
        
        write_step("Another way to think about this problem is to ask which end of the number line is closer to " + number + ".");
        write_step("Looking at the number line, we see that the correct answer is " + answer + ".");
    }
    
    function roundToPosition(num, pos){
        var factor = Math.pow(10, -1 * pos).toFixed(5);
        return Math.round(num * factor) / factor;
    }
    
    this.initGraphHints = function() {
        present.initPicture(x_min, x_max, y_min, y_max);
        present.fontfill = nColor;
        present.fontsize = 25;
        present.fontstyle = "normal";
        present.fontfamily = "Arial";
        present.fontsize = 17;
    }
    
    this.showGraphHints = function(hint_num) {
        if (hint_num < 4 || hint_num > 4)
            return;
        // Draw horizontal line        
        present.line([num_line_padding, num_line_y], [x_max - num_line_padding, num_line_y]);

        if (answer > number)
            first_tick = answer - Math.pow(10, type.pos);
        else
            first_tick = answer;

        // Draw vertical tick marks
        var total_distance = x_max - 2 * num_line_padding;
        var tick_distance = total_distance / 10;
        for (var i = 0; i < 11; i++) {
            var x = num_line_padding + i * tick_distance;
            present.line([x, num_line_y - tick_height / 2], [x, num_line_y + tick_height / 2]);
            var label = first_tick + i * Math.pow(10, type.pos - 1);
            label = roundToPosition(label, type.pos-1);
            present.text([x, num_line_y - tick_height], label);
        }
        
        // Draw number
        present.marker = "dot";
        present.strokewidth = 5;
        present.markerfill = getNextColor();
        present.markerstroke = present.markerfill;
        present.stroke = present.markerstroke;
        present.dotradius = 4;
        present.fontfill = present.stroke;
        
        x = ((number - first_tick) / Math.pow(10, type.pos)) * total_distance;
        present.line([num_line_padding + x, num_line_y], [num_line_padding + x, num_line_y]);
        present.text([num_line_padding + x, num_line_y + tick_height], number);
    }
}


