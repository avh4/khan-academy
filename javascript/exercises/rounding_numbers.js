// Rounding numbers
// Author: Marcia Lee
// Date: 2011-04-20
//
// Problem speclet:
//  Round X to the nearest {hundredth, tenth, one, ten, hundred, thousand}.
//  In the case of the first three, the number is between 10-99 and has 3 decimals.
//  For the last two, the number is between 100-999.
//

function RoundingExercise() {
    var number;
    var number_str;
    var round_index;
    var right_index;
    var rounding_num;
    var num_to_right;
    var answer;
    
    RoundingType = [{pos: -2, str: "hundredth"},
                    {pos: -1, str: "tenth"},
                    {pos: 0, str: "one"},
                    {pos: 1, str: "ten"},
                    {pos: 2, str: "hundred"},
                    {pos: 3, str: "thousand"}
                    ]
    
    generateProblem();
    showProblem();

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
        
        round_index = index - type.pos - (type.pos == 0 ? 1 : 0);
        right_index = index - type.pos + 1;
        
        rounding_num = number_str[round_index];
        num_to_right = number_str[right_index];
        
        answer = roundToPosition(number, type.pos);
        setCorrectAnswer(answer);
    }
    
    function showProblem() {
        write_text("Round " + number_str + " to the nearest " + type.str + ".");
    }

    function roundToPosition(num, pos){
        var factor = Math.pow(10, -1 * pos).toFixed(5);
        return Math.round(num * factor) / factor;
    }
    
    var x_max = 700;
    var y_max = 300;
    var num_line_padding = 20;
    var num_line_y = 250;
    var tick_height = 15;
    var round_color = getNextColor();
    var right_color = getNextColor();
    
    this.showGraphHints = function(hint_num) {
        var hint = "";
        var paper = present.paper;
        switch (hint_num) {
            case 0:
                for (var i = 0; i < number_str.length; i++) {
                    var font_attrs = {"font-size": 30};
                    if (i == round_index) {
                        font_attrs.stroke = round_color;
                        font_attrs.fill = round_color;
                    } else if (i == right_index) {
                        font_attrs.stroke = right_color;
                        font_attrs.fill = right_color;
                    }
                    paper.text(20 + i * 20, 20, number_str[i]).attr(font_attrs);
                }
                break;
            case 1:
                hint = "There are two ways to think about this problem.";
                break;
            case 2:
                hint = "1st way: Notice that the digit in the " + type.str + "s place is " + rounding_num
                            + " and that the digit to the right is " + num_to_right + ".";
                break;
            case 3:
                if (num_to_right >= 5)
                    hint = "Since the digit to the right (the " + num_to_right + ") is greater than or equal to 5, we should round up to " + answer + ".";
                else
                    hint = "Since the digit to the right (the " + num_to_right + ") is less than 5, we should round down to " + answer + ".";
                break;
            case 4:
                hint = "2nd way: Consider which end of the number line is closer to " + number + ".";
                break;
            case 5: 
                hint = "Looking at the number line, we see that the correct answer is indeed " + answer + ".";
                break;
            default:
        }

        if (hint_num >= 1 && hint_num <= 5)
            paper.text(20, 30 + (hint_num) * 30, hint).attr({"font-size": 15, "text-anchor": "start"});
        
        if (hint_num == 4) {
            // Draw horizontal line
            paper.path("M" + num_line_padding + " " + num_line_y + " L" + (x_max - num_line_padding) + " " + num_line_y);

            if (answer > number)
                first_tick = answer - Math.pow(10, type.pos);
            else
                first_tick = answer;

            // Draw vertical tick marks
            var total_distance = x_max - 2 * num_line_padding;
            var tick_distance = total_distance / 10;
            for (var i = 0; i < 11; i++) {
                var x = num_line_padding + i * tick_distance;
                paper.path("M" + x + " " + (num_line_y - tick_height / 2) + " L" + x + " " + (num_line_y + tick_height /2));
                var label = first_tick + i * Math.pow(10, type.pos - 1);
                label = roundToPosition(label, type.pos-1);
                paper.text(x, num_line_y + tick_height, label).attr({"font-size": 15});
            }
        
            // Draw number
            x = num_line_padding + ((number - first_tick) / Math.pow(10, type.pos)) * total_distance;
            var color = getNextColor();
            paper.circle(x, num_line_y, 8).attr({"fill": color, "stroke": color});
            paper.text(x, num_line_y - 1.5 * tick_height, number).attr({"font-size": 20, "stroke": color, "fill": color});
        }
    }
}


