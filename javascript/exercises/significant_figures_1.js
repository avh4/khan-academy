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
    
    function generateProblem() {
        if (getRandomIntRange(0, 5))
            number_str = generateNormalNumber();
        else
            number_str = generateZeroNumber();
            
        answer = countNumSigFig(number_str);
        setCorrectAnswer(answer);
        write_text("How many significant figures does " + number_str + " have?");
    }

    function generateNormalNumber() {
        var result = "";
        var num_leading_zeros = getRandomIntRange(0, 2) ? 0 : getRandomIntRange(1, 2);
        var num_trailing_zeros = getRandomIntRange(0, 2) ? 0 : getRandomIntRange(1, 2);
        var num_between = 6 - num_leading_zeros - num_trailing_zeros;
        var decimal;
        
        for (var i = 0; i < num_leading_zeros; i++)
            result += "0";
        for (var i = 0; i < num_between; i++)
            result += !getRandomIntRange(0, 2) ? 0 : getRandomIntRange(1, 9);
        for (var i = 0; i < num_trailing_zeros; i++)
            result += "0";
            
        if (result[0] == "0")
            decimal = 1;
        else
            decimal = getRandomIntRange(-3, result.length);
            
        if (decimal >= 0)
            result = result.substring(0, decimal) + "." + result.substring(decimal);
            
        return result;
    }

    function generateZeroNumber() {
        // To generate the trickier numbers like 0.00 or just plain old 0
        var result = "0";
        var num_zeros = getRandomIntRange(1, 3);
        if (num_zeros != 1) {
            result += ".";
            for (var i = 1; i < num_zeros; i++)
                result += "0";
        }
        return result;
    }
    
    function countNumSigFig(str) {
        index_first_non_zero = 0;
        index_last_non_zero = number_str.length - 1;
        index_decimal = str.indexOf(".");
        // Special case if the entire number is zeros
        if (number_str.search(/[1-9]/) == -1) {
            if (index_decimal == -1)
                return 1;
            else
                return number_str.length - index_decimal;
        }
        
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
            if (i != index_decimal) 
                raphael_numbers[i].attr({"font-size": 30, "stroke": color, "fill": color});
        }
    }

    function showNumber() {
        for (var i = 0; i < number_str.length; i++) {
            raphael_numbers[raphael_numbers.length] = present.paper.text(10 + i * 20, 20, number_str[i]).attr({"font-size": 30});
        }        
    }
    
    function getSignificantHint() {
        var hint;
        if (number_str.search(/[1-9]/) == -1) {
            if (index_decimal == -1) {
                hint = "In this special case with only zeros and no decimal, there is 1 significant figure.";
                highlightNum(number_str.length - 1, number_str.length, color_sig);
            } else {
                hint = "In this special case with only zeros and a decimal, all " + answer + " zeros are significant.";
                raphael_numbers[index_decimal].attr({"font-size": 30, "stroke": color_decimal, "fill": color_decimal}); 
                highlightNum(0, number_str.length, color_sig);
            }
            optional_hints_given[0] = true;
            optional_hints_given[1] = true;
        } else {
            hint = "Identify the non-zero digits and any zeros between them. These are all significant.";
            highlightNum(index_first_non_zero, index_last_non_zero + 1, color_sig);                    
        }
        return hint;
    }
    
    function getLeadingHint() {
        highlightNum(0, index_first_non_zero, color_leading);
        return "Leading zeros are not significant.";
    }
    
    function getTrailingHint() {
        var hint;
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
        return hint;
    }
    
    function getFinalHint() {
        optional_hints_given[1] = true;
        return number_str + " has " + answer + " significant figure" + (answer == 1 ? "" : "s") + ".";
    }
    
    this.showGraphHints = function(hint_num) {
        var hint = "";

        switch (hint_num) {
            case 0:
                showNumber();
                break;
            case 1:
                hint = getSignificantHint();
                break;
            case 2:
                if (index_first_non_zero) {
                    hint = getLeadingHint();
                    break;
                }
            case 3:
                if (index_last_non_zero != number_str.length - 1 && !optional_hints_given[0]){
                    hint = getTrailingHint();
                    break;
                }
            case 4:
                if (!optional_hints_given[1]) {
                    hint = getFinalHint();
                }
            default:
        }

        if (hint_num > 0 && hint_num < 5 && !done_hinting) {
            present.paper.text(10, 30 + (hint_num) * 30, hint).attr({"font-size": 15, "text-anchor": "start"});
            if (optional_hints_given[1])
                done_hinting = true;
        }
    }
}


