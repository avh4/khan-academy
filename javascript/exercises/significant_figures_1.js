// Significant figures 1
// Author: Marcia Lee
// Date: 2011-04-22
//
// Problem speclet:
//  Just so you know, since I'd forgotten:
//  Non-zero digits are significant
//  Zeros between non-zeros are significant
//  Leading zeros are NOT significant
//  If there is a decimal, trailing zeros are significant
//  In other words, if there is no decimal, trailing zeros are not significant
//


function SigFig1Exercise() {
    var number_str = "";
    var answer;
    var index_first_non_zero;
    var index_last_non_zero;
    var index_decimal;
    
    generateProblem();
    showProblem();

    function generateProblem() {
        var num_leading_zeros = getRandomIntRange(0, 2) ? 0 : getRandomIntRange(1, 2);
        var num_trailing_zeros = getRandomIntRange(0, 2) ? 0 : getRandomIntRange(1, 2);

        // 0.000X is tricky, so let's throw this in 1/6 of the time.
        if (!getRandomIntRange(0, 5)) {
            num_leading_zeros = 5;
            num_trailing_zeros = 0;
        }
        
        var num_between = 6 - num_leading_zeros - num_trailing_zeros;
        
        for (var i = 0; i < num_leading_zeros; i++)
            number_str += "0";

        for (var i = 0; i < num_between; i++)
            number_str += !getRandomIntRange(0, 2) ? 0 : getRandomIntRange(1, 9);
            
        for (var i = 0; i < num_trailing_zeros; i++)
            number_str += "0";
            
        var decimal = 0;
        if (number_str[0] == "0")
            decimal = 1;
        else
            decimal = getRandomIntRange(-3, number_str.length);
            
        if (decimal >= 0)
            number_str = number_str.substring(0, decimal) + "." + number_str.substring(decimal);
        
        // Right now, don't allow for 0.00000 :(
        if (number_str.search(/[1-9]/) == -1) {
            number_str = number_str.substring(0, number_str.length - 1) + getRandomIntRange(1, 9);
        }
            
        index_first_non_zero = 0;
        index_last_non_zero = number_str.length - 1;
        answer = countNumSigFig(number_str);
        setCorrectAnswer(answer);
    }
    
    function showProblem() {
        write_text("How many significant figures does " + number_str + " have?");
    }
    
    function countNumSigFig(str) {
        // Find first non zero char (to ignore leading zeros)
        for (; index_first_non_zero < str.length; index_first_non_zero++) {
            var c = str[index_first_non_zero];
            if (c != "0" && c != ".")
                break;
        }

        // Find last non zero char (to maybe ignore trailing zeros)
        for (; index_last_non_zero >= 0; index_last_non_zero--) {
            var c = str[index_last_non_zero];
            if (c != "0" && c != ".")
                break;
        }

        // If there is a decimal, count trailing zeros
        index_decimal = str.indexOf(".");
        if (index_decimal == -1)
            return index_last_non_zero - index_first_non_zero + 1;
        else if (index_decimal > index_first_non_zero)
            return str.length - index_first_non_zero - 1;
        else
            return str.length - index_first_non_zero;
    }

    var color_leading = "orange";
    var color_sig = "blue";
    var color_trailing = "brown";
    var color_decimal = "red";
    var raphael_numbers = [];
    var optional_hints_given = [false, false];
    var done_hinting = false;
    
    function highlightNum(start, end, color) {
        for (var i = start; i < end; i++) {
            if (i == index_decimal) continue;
            raphael_numbers[i].attr({"font-size": 30, "stroke": color, "fill": color});
        }
    }

    this.showGraphHints = function(hint_num) {
        var hint = "";
        var paper = present.paper;

        switch (hint_num) {
            case 0:
                for (var i = 0; i < number_str.length; i++) {
                    raphael_numbers[raphael_numbers.length] = paper.text(10 + i * 20, 20, number_str[i]).attr({"font-size": 30});
                }
                break;
            case 1:
                hint = "Identify the non-zero digits and any zeros between them. These are all significant.";
                highlightNum(index_first_non_zero, index_last_non_zero + 1, color_sig);
                break;
            case 2:
                if (index_first_non_zero) {
                    hint = "Leading zeros are not significant.";
                    highlightNum(0, index_first_non_zero, color_leading);
                    break;
                }
            case 3:
                if (index_last_non_zero + 1 != number_str.length && !optional_hints_given[0]){
                    if (index_decimal == -1) {
                        hint = "Since there is no decimal, trailing zeros are not significant."
                        color = color_trailing;                        
                    } else {
                        hint = "Since there is a decimal, trailing zeros are significant."
                        color = color_sig;  
                        raphael_numbers[index_decimal].attr({"font-size": 30, "stroke": color_decimal, "fill": color_decimal});   
                    }
                    highlightNum(index_last_non_zero + 1, number_str.length, color);
                    optional_hints_given[0] = true;
                    break;                   
                }
            case 4:
                if (!optional_hints_given[1]) {
                    hint = number_str + " has " + answer + " significant figure" + (answer == 1 ? "" : "s") + ".";
                    optional_hints_given[1] = true;
                    break;                    
                }
            default:
        }

        if (hint_num > 0 && hint_num < 5 && !done_hinting) {
            paper.text(10, 30 + (hint_num) * 30, hint).attr({"font-size": 15, "text-anchor": "start"});
            if (optional_hints_given[1])
                done_hinting = true;
        }
    }
}


