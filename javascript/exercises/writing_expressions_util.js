function Expression() {
    var coeff = get_random();
    var inner = "x";
    var constant = get_random();
    
    var product_clause = new ProductClause();
    var sum_clause = new SumClause();
    
    this.getCoefficient = function() {
        return coeff;
    }
    
    this.getInner = function() {
        return inner;
    }
    
    this.getConstant = function() {
        return constant;
    }
    
    this.setCoefficient = function(new_coeff) {
        coeff = new_coeff;
    }
    
    this.setInner = function(new_inner) {
        inner = new_inner;
    }
    
    this.setConstant = function(new_constant) {
        constant = new_constant;
    }
    
    this.equals = function (other_expression) {
        var inner_is_equal = false;
        if (inner.equals instanceof Function && other_expression.getInner().equals instanceof Function)
            inner_is_equal = inner.equals(other_expression.getInner());
        else if (inner.equals instanceof Function || other_expression.getInner().equals instanceof Function)
            return false;
        else
            inner_is_equal = inner == other_expression.getInner();
            
        return coeff == other_expression.getCoefficient() && constant == other_expression.getConstant();
    }
    
    this.toString = function() {
        var inner_str = inner.toString();
        if (inner_str.length != 1)
            inner_str = "(" + inner_str + ")";
        return "" + format_first_coefficient(coeff) + inner_str + format_constant(constant);
    }
    
    this.toEnglish = function() {
        if (inner.toEnglish instanceof Function)
            product_clause.init(coeff, "that expression");
        else
            product_clause.init(coeff.toString(), inner.toString());
        sum_clause.init(constant, product_clause.toEnglish());
        return sum_clause.toEnglish();
    }
    
    this.toClauses = function() {
        if (sum_clause.isReversed())
            return {first: sum_clause.getSecondPhrase(), second: sum_clause.getFirstPhrase(), firstClauseStandsAlone: true};
        else
            return {first: sum_clause.getFirstPhrase(), second: sum_clause.getSecondPhrase(), firstClauseStandsAlone: false};
    }
    
    this.showHints = function() {
        var clauses = this.toClauses();
        if (inner.showHints instanceof Function)
            inner.showHints();

        var first_clause = format_string_with_color(clauses.first, "blue");
        var second_clause = format_string_with_color(clauses.second, "orange");    

        write_step("What is " + second_clause + "?");
        
        var inner_str = inner.toString();
        if (inner_str.length != 1)
            inner_str = "(" + inner_str  + ")";
        var first_term = format_math_with_color(format_first_coefficient(coeff) + inner_str, "orange");
            
        write_step("`" + coeff + " * " + inner_str + " = ` "+ first_term);
        
        if (clauses.firstClauseStandsAlone)
            write_step("What " + first_clause + "?");
        else 
            write_step("What is " +  first_clause + " " + first_term + "?");
        
        var second_term = format_math_with_color(format_constant(constant), "blue");
        write_step(first_term + second_term);
    }
}

function ProductClause() {
    var f1;
    var f2;
    var type = get_random() > 0;

    this.init = function(first_factor, second_factor) {
        f1 = first_factor;
        f2 = second_factor;
    }
    
    this.toEnglish = function() {
        if (type)
            return " the product of " + f1 + " and " + f2;
        else
            return " the quantity " + f1 + " times " + f2;
    }
}

function SumClause() {
     var t1;
     var t2;
     var type = getRandomInt(2);

     var first_phrase;
     var second_phrase;
     
     this.init = function(first_term, second_term) {
         t1 = first_term;
         t2 = second_term;

         switch (type) {
             case 0:
                 first_phrase = " the sum of " + t1 + " and ";
                 second_phrase = t2;
                 english = first_phrase + second_phrase + ". ";
                 break;
             case 1:
                 first_phrase = t1 + " plus ";
                 second_phrase = t2;
                 english = first_phrase + second_phrase + ". ";
                 break;
             default:
                first_phrase = t2;
                second_phrase = " then add " + t1;
                english = " Take " + first_phrase + ", and " + second_phrase + ".";
                second_phrase = " does adding " + t1 + " do";
         }
     }
     
     this.isReversed = function() {
         return type == 2;
     }
     
     this.toEnglish = function() {
         return english;
     }
     
     this.getFirstPhrase = function() {
         return first_phrase;
     }
     
     this.getSecondPhrase = function() {
         return second_phrase;
     }
 }
